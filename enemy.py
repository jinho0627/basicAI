# enemy.py
"""
B팀 담당: 적 생성, 이동, 적 추적 AI 및 게임 난이도 조절
이 모듈은 게임 내의 적(Enemy) 캐릭터의 FSM(유한 상태 머신) 행동 패턴을 정의하고,
난이도별 스펙 조절 및 전체 적 목록을 관리하는 매니저 클래스를 제공합니다.
"""

import math
from enum import Enum
from pathfinding import a_star

class EnemyState(Enum):
    PATROL = 1  # 순찰 상태
    CHASE = 2   # 플레이어 추적 상태
    ATTACK = 3  # 플레이어 공격 상태
    DEAD = 4    # 사망 상태


class Enemy:
    def __init__(self, x, y, base_hp=100, base_speed=1.5, base_damage=10, base_attack_range=1.2, base_detection_range=8.0):
        # 월드 좌표 (실수 값)
        self.x = x
        self.y = y
        
        # 난이도 조절이 적용된 최종 속성값들
        self.max_hp = base_hp
        self.hp = base_hp
        self.speed = base_speed
        self.damage = base_damage
        self.attack_range = base_attack_range
        self.detection_range = base_detection_range
        
        # 상태 관리
        self.state = EnemyState.PATROL
        
        # 공격 주기 관리 (초 단위)
        self.attack_cooldown = 0.0
        self.attack_rate = 1.0  # 1초에 1번 공격 가능
        
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
        self.current_patrol_idx = 0

    def take_damage(self, amount):
        """C팀의 총 발사(weapon.py) 등에서 호출하는 피격 인터페이스입니다."""
        if self.state == EnemyState.DEAD:
            return 0
        
        self.hp -= amount
        # 피해를 받으면 즉시 플레이어 추적 상태(CHASE)로 강제 변환 (AI 반응성 향상)
        if self.state == EnemyState.PATROL:
            self.state = EnemyState.CHASE
            
        if self.hp <= 0:
            self.hp = 0
            self.state = EnemyState.DEAD
            return self.damage * 2  # 사망 시 추가 처치 점수 등으로 활용할 값 반환
        return amount

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

    def attack_behavior(self, player_pos, dt):
        """공격 범위 내에서의 행동 패턴"""
        self.path = []  # 공격 중에는 경로 탐색 중단
        
        if self.attack_cooldown <= 0:
            # 공격 실행
            self.attack_cooldown = self.attack_rate
            # C팀의 game_state.py/player.py 등에서 플레이어 HP 깎기 처리가 가능하도록 로그 출력
            # 실제 게임 통합 시 여기에 player.take_damage(self.damage) 또는 game_state.damage_player(self.damage)를 호출합니다.
            print(f"[AI ATTACK] 적이 플레이어에게 {self.damage} 만큼의 피해를 입혔습니다!")

    def chase_behavior(self, player_pos, grid_map, dt):
        """A* 알고리즘을 이용해 플레이어를 추적하는 행동 패턴"""
        self.path_update_timer += dt
        
        # 실시간 경로 재계산 (비용 절감을 위해 주기적 갱신)
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0.0
            
            # 본인과 플레이어의 월드 좌표를 그리드 좌표로 변환
            start_grid = (int(self.x), int(self.y))
            goal_grid = (int(player_pos[0]), int(player_pos[1]))
            
            self.path = a_star(grid_map, start_grid, goal_grid)

        # 경로가 존재하면 경로를 따라 이동
        if self.path and len(self.path) > 1:
            # 바로 현재 타일이 아닌, '다음 타일'의 중심점을 목표로 이동
            target_grid = self.path[1]
            target_x = target_grid[0] + 0.5
            target_y = target_grid[1] + 0.5
            
            self.move_towards(target_x, target_y, grid_map, dt)
        else:
            # 경로가 끊겼거나 구하지 못한 경우, 직선으로 플레이어를 향해 단순 이동 시도
            self.move_towards(player_pos[0], player_pos[1], grid_map, dt)

    def patrol_behavior(self, grid_map, dt):
        """플레이어가 감지 범위 밖에 있을 때 정해진 경로를 돌거나 스폰지점 주변을 도는 행동 패턴"""
        if not self.patrol_points:
            # 순찰 지점이 없으면 스폰 지점 부근에서 무작위 타일들을 순찰하도록 예시 포인트 설정
            sx, sy = self.spawn_pos
            self.patrol_points = [
                (sx, sy),
                (sx + 1, sy),
                (sx + 1, sy + 1),
                (sx, sy + 1)
            ]
            
        target_pt = self.patrol_points[self.current_patrol_idx]
        tx, ty = target_pt[0] + 0.5, target_pt[1] + 0.5
        
        # 목표 순찰점에 충분히 근접했는지 체크
        dist = math.sqrt((tx - self.x)**2 + (ty - self.y)**2)
        if dist < 0.2:
            self.current_patrol_idx = (self.current_patrol_idx + 1) % len(self.patrol_points)
        
        # 경로 탐색 기반으로 순찰점 이동
        self.path_update_timer += dt
        if self.path_update_timer >= self.path_update_interval or not self.path:
            self.path_update_timer = 0.0
            start_grid = (int(self.x), int(self.y))
            goal_grid = (int(tx), int(ty))
            self.path = a_star(grid_map, start_grid, goal_grid)

        if self.path and len(self.path) > 1:
            next_step = self.path[1]
            self.move_towards(next_step[0] + 0.5, next_step[1] + 0.5, grid_map, dt)
        else:
            self.move_towards(tx, ty, grid_map, dt)

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
            
            # 충돌 검사 (간단한 원형 충돌 판정 및 슬라이딩 처리)
            new_x = self.x + nx * move_step
            new_y = self.y + ny * move_step
            
            # X축 이동 검사
            if not grid_map.is_wall(new_x, self.y):
                self.x = new_x
            # Y축 이동 검사
            if not grid_map.is_wall(self.x, new_y):
                self.y = new_y


class EnemyManager:
    def __init__(self, difficulty='medium'):
        self.enemies = []
        self.difficulty = difficulty.lower()
        
        # 난이도 조절 설정 테이블 (체력 배율, 속도 배율, 공격력 배율)
        self.difficulty_settings = {
            'easy':   {'hp_mult': 0.6, 'speed_mult': 0.7, 'dmg_mult': 0.5, 'detect_mult': 0.8},
            'medium': {'hp_mult': 1.0, 'speed_mult': 1.0, 'dmg_mult': 1.0, 'detect_mult': 1.0},
            'hard':   {'hp_mult': 1.5, 'speed_mult': 1.3, 'dmg_mult': 1.5, 'detect_mult': 1.3}
        }

    def set_difficulty(self, difficulty):
        """게임 진행 중 난이도가 변경될 경우 일괄 적용할 수 있는 인터페이스입니다. (C팀 연동)"""
        self.difficulty = difficulty.lower()
        if self.difficulty not in self.difficulty_settings:
            self.difficulty = 'medium'
            
        settings = self.difficulty_settings[self.difficulty]
        # 이미 스폰된 살아있는 적들의 스펙도 난이도 비율에 맞춰 실시간 재조정
        for enemy in self.enemies:
            if enemy.state != EnemyState.DEAD:
                # 기본값 100 기준
                enemy.max_hp = int(100 * settings['hp_mult'])
                enemy.hp = min(enemy.hp, enemy.max_hp)
                enemy.speed = 1.5 * settings['speed_mult']
                enemy.damage = int(10 * settings['dmg_mult'])
                enemy.detection_range = 8.0 * settings['detect_mult']

    def spawn_enemies(self, map_obj):
        """map.py의 enemy_spawns 정보를 바탕으로 난이도를 적용하여 적들을 스폰시킵니다."""
        self.enemies.clear()
        settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings['medium'])
        
        for spawn_x, spawn_y in map_obj.enemy_spawns:
            hp = int(100 * settings['hp_mult'])
            speed = 1.5 * settings['speed_mult']
            damage = int(10 * settings['dmg_mult'])
            detection = 8.0 * settings['detect_mult']
            
            enemy = Enemy(
                x=spawn_x,
                y=spawn_y,
                base_hp=hp,
                base_speed=speed,
                base_damage=damage,
                base_detection_range=detection
            )
            
            # 스폰 근처에 임의의 순찰 지점 설정 (스폰 타일 주변 상하좌우)
            cx, cy = int(spawn_x), int(spawn_y)
            patrol_pts = [(cx, cy)]
            # 맵 범위를 확인하며 순찰 가능 타일들을 찾아 추가
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

    def get_active_enemies(self):
        """살아있는 적들만 필터링하여 반환합니다. 렌더링 및 C팀 무기 사격 충돌 판정에 사용됩니다."""
        return [enemy for enemy in self.enemies if enemy.state != EnemyState.DEAD]
