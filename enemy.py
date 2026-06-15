# enemy.py
"""
B팀 담당: 적 생성, 이동, 적 추적 AI 및 게임 난이도 조절
이 모듈은 게임 내의 적(Enemy) 캐릭터의 FSM(유한 상태 머신) 행동 패턴을 정의하고,
난이도별 스펙 조절 및 전체 적 목록을 관리하는 매니저 클래스를 제공합니다.

학점별 적 스펙:
  - F학점: 체력 2배, 공격력 2배, 근접 공격, 적게 스폰 (처치 점수 300)
  - D학점: C와 동일 스펙, 근접 공격 없이 원거리(공기포)만 사용 (처치 점수 200)
  - C학점: 기본 스펙, 근접 공격 (처치 점수 100)

난이도 배율 (easy / medium / hard):
  - 적 체력 배율: 1.0 / 1.5 / 2.0
  - 처치 점수 배율: 1.0 / 1.5 / 2.0
"""

import math
from enum import Enum
from pathfinding import a_star


class EnemyState(Enum):
    PATROL = 1  # 순찰 상태
    CHASE = 2   # 플레이어 추적 상태
    ATTACK = 3  # 플레이어 공격 상태
    DEAD = 4    # 사망 상태


# ─── 학점별 기본 스펙 테이블 ──────────────────────────────────────────────────
# C학점을 기준(base)으로 F학점은 체력·공격력 2배
GRADE_SPECS = {
    'C': {'hp': 70,  'speed': 1.1, 'damage': 8,  'attack_range': 1.2, 'detection_range': 8.0, 'score': 100},
    'D': {'hp': 70,  'speed': 1.1, 'damage': 8,  'attack_range': 0.0, 'detection_range': 8.0, 'score': 200},  # 근접 공격 없음
    'F': {'hp': 140, 'speed': 1.4, 'damage': 16, 'attack_range': 1.2, 'detection_range': 8.0, 'score': 300},
}


class Projectile:
    """D학점 적이 발사하는 원거리 공기포 투사체"""
    RADIUS = 0.15  # 플레이어 충돌 판정 반지름

    def __init__(self, x, y, vx, vy, damage=8):
        self.x = x
        self.y = y
        self.vx = vx   # 정규화된 방향 벡터
        self.vy = vy
        self.speed = 5.0
        self.damage = damage
        self.alive = True
        self.lifetime = 5.0  # 5초 후 자동 소멸

    def update(self, grid_map, dt):
        """투사체를 한 프레임 전진시키고 벽 충돌을 검사합니다."""
        if not self.alive:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        new_x = self.x + self.vx * self.speed * dt
        new_y = self.y + self.vy * self.speed * dt
        if grid_map.is_wall(new_x, new_y):
            self.alive = False
            return
        self.x = new_x
        self.y = new_y


class Enemy:
    def __init__(self, x, y, grade='C', hp_mult=1.0, score_mult=1.0):
        """
        적 캐릭터를 생성합니다.

        Parameters:
            x, y (float): 월드 좌표 (실수 값)
            grade (str): 학점 등급 ('F', 'D', 'C')
            hp_mult (float): 난이도에 따른 체력 배율
            score_mult (float): 난이도에 따른 점수 배율
        """
        # 월드 좌표 (실수 값)
        self.x = x
        self.y = y

        # 학점 구분 ('F', 'D', 'C')
        self.grade = grade

        # 학점별 기본 스펙 가져오기
        spec = GRADE_SPECS.get(grade, GRADE_SPECS['C'])

        # 난이도 배율이 적용된 최종 속성값들
        self.max_hp = int(spec['hp'] * hp_mult)
        self.hp = self.max_hp
        self.speed = spec['speed']
        self.damage = spec['damage']
        self.attack_range = spec['attack_range']
        self.detection_range = spec['detection_range']
        self.radius = 0.25  # 벽 충돌 방지를 위한 반지름 크기

        # 처치 점수 (난이도 배율 적용)
        self.kill_score = int(spec['score'] * score_mult)

        # 상태 관리
        self.state = EnemyState.PATROL

        # 근접 공격 주기 관리 (초 단위) - D학점은 근접 공격 없음
        self.attack_cooldown = 0.0
        self.attack_rate = 1.0  # 1초에 1번 공격 가능

        # D학점 원거리(공기포) 공격 관련
        self.shoot_cooldown = 0.0
        self.shoot_rate = 2.5     # 2.5초마다 1발 발사
        self.ranged_range = 6.0   # 이 거리 이내이면 공기포 발사
        self.pending_projectiles = []  # 이번 프레임에 생성할 투사체 대기열

        # 순찰 및 경로 탐색 관련
        self.patrol_points = []
        self.current_patrol_idx = 0
        self.path = []            # A* 알고리즘으로 계산된 그리드 경로 리스트
        self.path_update_timer = 0.0 # A* 계산 빈도를 줄이기 위한 타이머
        self.path_update_interval = 0.5 # 0.5초마다 경로 갱신

        # 생성 시점의 좌표를 최초 순찰 기준으로 등록
        self.spawn_pos = (x, y)

    def set_patrol_points(self, points):
        """적의 순찰 경로점들을 설정합니다."""
        self.patrol_points = points

    def take_damage(self, amount):
        """
        외부(C팀 무기 시스템)로부터 피해를 받았을 때 호출됩니다.
        사망 시 처치 점수를 반환합니다.
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.state = EnemyState.DEAD
            return self.kill_score  # 사망 시 처치 점수 반환
        return 0

    def update(self, player_pos, grid_map, dt):
        """
        매 프레임 적의 상태 전이(FSM)와 움직임을 업데이트합니다.

        Parameters:
            player_pos (tuple): 플레이어의 현재 월드 좌표 (x, y)
            grid_map (Map): map.py의 Map 인스턴스
            dt (float): 델타 타임 (초 단위)
        """
        if self.state == EnemyState.DEAD:
            return

        px, py = player_pos
        dx = px - self.x
        dy = py - self.y
        dist_to_player = math.sqrt(dx**2 + dy**2)

        # 1. 상태 전이 로직 (FSM)
        if self.grade == 'D':
            # D학점은 근접 공격이 없으므로 attack_range=0 → ATTACK 상태 진입 안 함
            if dist_to_player <= self.detection_range:
                self.state = EnemyState.CHASE
            else:
                self.state = EnemyState.PATROL
        else:
            # F, C 학점: 근접 공격 가능
            if dist_to_player <= self.attack_range:
                self.state = EnemyState.ATTACK
            elif dist_to_player <= self.detection_range:
                self.state = EnemyState.CHASE
            else:
                self.state = EnemyState.PATROL

        # 2. 상태별 행동 수행 및 이동 처리
        if self.state == EnemyState.ATTACK:
            self.attack_behavior(player_pos, dt)
        elif self.state == EnemyState.CHASE:
            self.chase_behavior(player_pos, grid_map, dt)
        elif self.state == EnemyState.PATROL:
            self.patrol_behavior(grid_map, dt)

        # 3. 공격 쿨다운 타이머 업데이트
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # 4. D학점 원거리 공기포 발사 (CHASE 상태에서 사거리 내에 있을 때)
        if self.grade == 'D' and self.state == EnemyState.CHASE:
            self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
            if self.shoot_cooldown <= 0 and dist_to_player <= self.ranged_range:
                self.shoot_cooldown = self.shoot_rate
                safe_dist = max(dist_to_player, 0.01)
                proj = Projectile(
                    self.x, self.y,
                    dx / safe_dist, dy / safe_dist,
                    damage=self.damage
                )
                self.pending_projectiles.append(proj)

    def attack_behavior(self, player_pos, dt):
        """근접 공격 범위 내에서의 행동 패턴 (F, C 학점 전용)"""
        self.path = []  # 공격 중에는 경로 탐색 중단

        if self.attack_cooldown <= 0:
            # 공격 실행
            self.attack_cooldown = self.attack_rate
            print(f"[AI ATTACK] {self.grade}학점 적이 플레이어에게 {self.damage} 만큼의 피해를 입혔습니다!")

    def chase_behavior(self, player_pos, grid_map, dt):
        """A* 알고리즘을 이용해 플레이어를 추적하는 행동 패턴"""
        self.path_update_timer += dt

        # 실시간 경로 재계산 (비용 절감을 위해 주기적 갱신)
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0.0

            start = (int(self.x), int(self.y))
            goal = (int(player_pos[0]), int(player_pos[1]))

            new_path = a_star(grid_map, start, goal)
            if new_path:
                self.path = new_path

        # 경로를 따라 이동
        if self.path:
            tx, ty = self.path[0]
            target_x = tx + 0.5  # 타일 중앙 좌표
            target_y = ty + 0.5

            dist = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
            if dist < 0.3:
                self.path.pop(0)  # 다음 경유 지점으로 이동
                if self.path:
                    tx, ty = self.path[0]
                    target_x = tx + 0.5
                    target_y = ty + 0.5
                else:
                    return
            self.move_towards(target_x, target_y, grid_map, dt)
        else:
            # 경로가 없으면 플레이어 방향으로 직접 이동 시도
            self.move_towards(player_pos[0], player_pos[1], grid_map, dt)

    def patrol_behavior(self, grid_map, dt):
        """순찰 경로점들을 순서대로 이동하는 행동 패턴"""
        if not self.patrol_points:
            return

        target = self.patrol_points[self.current_patrol_idx]
        tx, ty = target[0] + 0.5, target[1] + 0.5

        dist = math.sqrt((tx - self.x)**2 + (ty - self.y)**2)
        if dist < 0.3:
            self.current_patrol_idx = (self.current_patrol_idx + 1) % len(self.patrol_points)
        else:
            self.move_towards(tx, ty, grid_map, dt)

    def can_move_to(self, new_x, new_y, grid_map):
        """
        새로운 좌표 (new_x, new_y)로 이동 가능한지 검사합니다.
        적의 몸통 반지름(radius) 크기만큼의 사각형 꼭짓점 4곳을 모두 검사하여
        어느 한 곳이라도 벽에 닿으면 이동 불가를 반환합니다.
        """
        r = self.radius
        for cx, cy in [
            (new_x - r, new_y - r),
            (new_x + r, new_y - r),
            (new_x - r, new_y + r),
            (new_x + r, new_y + r),
        ]:
            if grid_map.is_wall(cx, cy):
                return False
        return True

    def move_towards(self, tx, ty, grid_map, dt):
        """목표 (tx, ty) 좌표를 향해 방향을 계산하여 벽과의 충돌을 피하며 한 단계 이동합니다."""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist > 0.01:
            # 방향 벡터 정규화
            nx = dx / dist
            ny = dy / dist

            # 이동할 양 계산
            move_step = self.speed * dt

            new_x = self.x + nx * move_step
            new_y = self.y + ny * move_step

            # 4꼭짓점 충돌 검사 + 슬라이딩: X/Y 각각 독립 검사
            # X축만 이동했을 때 가능한지 체크
            if self.can_move_to(new_x, self.y, grid_map):
                self.x = new_x
            # Y축만 이동했을 때 가능한지 체크
            if self.can_move_to(self.x, new_y, grid_map):
                self.y = new_y


class EnemyManager:
    """
    적 일괄 관리 매니저.
    난이도에 따른 스폰, 업데이트, 투사체 관리, 점수 계산을 담당합니다.
    """

    # 난이도별 배율 및 스폰 개수 테이블 (영어와 한국어 지원)
    DIFFICULTY_TABLE = {
        'easy':   {'hp_mult': 1.0, 'score_mult': 1.0, 'spawn_count': 5},
        'medium': {'hp_mult': 1.5, 'score_mult': 1.5, 'spawn_count': 10},
        'hard':   {'hp_mult': 2.0, 'score_mult': 2.0, 'spawn_count': 15},
        '쉬움':   {'hp_mult': 1.0, 'score_mult': 1.0, 'spawn_count': 5},
        '보통':   {'hp_mult': 1.5, 'score_mult': 1.5, 'spawn_count': 10},
        '어려움': {'hp_mult': 2.0, 'score_mult': 2.0, 'spawn_count': 15},
    }

    def __init__(self, difficulty='보통'):
        self.enemies = []
        self.projectiles = []  # 현재 날아다니는 투사체 목록
        self.difficulty = difficulty.lower()

    def set_difficulty(self, difficulty):
        """게임 진행 중 난이도 변경 인터페이스 (C팀 연동)"""
        if isinstance(difficulty, str):
            self.difficulty = difficulty.lower()
        else:
            self.difficulty = str(difficulty).lower()
        if self.difficulty not in self.DIFFICULTY_TABLE:
            self.difficulty = '보통'

    def spawn_enemies(self, map_obj):
        """
        map.py의 정보를 바탕으로 난이도별 스폰 개수와 스펙을 적용하여 적들을 스폰시킵니다.

        스폰 배치:
          - 쉬움 / easy (5마리): F 1마리, D 2마리, C 2마리
          - 보통 / medium (10마리): F 2마리, D 4마리, C 4마리
          - 어려움 / hard (15마리): F 3마리, D 6마리, C 6마리
        """
        self.enemies.clear()
        settings = self.DIFFICULTY_TABLE.get(self.difficulty, self.DIFFICULTY_TABLE['보통'])
        hp_mult = settings['hp_mult']
        score_mult = settings['score_mult']
        spawn_count = settings['spawn_count']

        # 맵에서 난이도에 해당하는 개수만큼의 스폰 포인트를 동적으로 생성합니다.
        spawns = map_obj.generate_enemy_spawns(num=spawn_count, min_dist=5)

        # F, D, C 학점 순으로 스펙에 맞게 배분 (F는 약 20%의 가장 적은 비율을 차지하도록 설정)
        f_count = max(1, spawn_count // 5)
        rem = spawn_count - f_count
        d_count = rem // 2
        c_count = rem - d_count

        grades = ['F'] * f_count + ['D'] * d_count + ['C'] * c_count

        for idx, (spawn_x, spawn_y) in enumerate(spawns):
            grade = grades[idx % len(grades)]

            enemy = Enemy(
                x=spawn_x,
                y=spawn_y,
                grade=grade,
                hp_mult=hp_mult,
                score_mult=score_mult,
            )

            # 스폰 근처에 순찰 지점 설정 (스폰 타일 주변 상하좌우)
            cx, cy = int(spawn_x), int(spawn_y)
            patrol_pts = [(cx, cy)]
            for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                px, py = cx + offset_x, cy + offset_y
                if not map_obj.is_out_of_bounds(px, py) and map_obj.grid[py][px] == 0:
                    patrol_pts.append((px, py))

            enemy.set_patrol_points(patrol_pts)
            self.enemies.append(enemy)

    def update_all(self, player_pos, map_obj, dt):
        """모든 적을 일괄 업데이트하며, 다른 팀원의 Game Loop(engine.py)에서 매 프레임 호출합니다."""
        for enemy in self.enemies:
            enemy.update(player_pos, map_obj, dt)
            # D학점 적이 생성한 투사체를 전역 목록으로 옮김
            if enemy.pending_projectiles:
                self.projectiles.extend(enemy.pending_projectiles)
                enemy.pending_projectiles.clear()

        # 투사체 이동 업데이트 및 소멸 처리
        for proj in self.projectiles:
            proj.update(map_obj, dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def check_projectile_hits(self, player_pos):
        """
        투사체가 플레이어에 맞았는지 검사하고, 맞은 투사체를 소멸시킨 후
        받은 총 피해량을 반환합니다. (Game Loop에서 매 프레임 호출)
        """
        px, py = player_pos
        total_damage = 0
        for proj in self.projectiles:
            if not proj.alive:
                continue
            dist = math.sqrt((proj.x - px)**2 + (proj.y - py)**2)
            if dist < Projectile.RADIUS + 0.3:  # 플레이어 반지름 0.3
                total_damage += proj.damage
                proj.alive = False
        return total_damage

    def clear_projectiles(self):
        """리스폰/리셋 시 모든 투사체를 제거합니다."""
        self.projectiles.clear()

    def get_active_enemies(self):
        """살아있는 적들만 필터링하여 반환합니다. 렌더링 및 C팀 무기 사격 충돌 판정에 사용됩니다."""
        return [enemy for enemy in self.enemies if enemy.state != EnemyState.DEAD]
