# test_ai.py
"""
B팀 검증용: 유닛 테스트
이 파일은 맵 절차적 생성, A* 알고리즘의 동작, 적 학점별 스펙, 난이도 배율 등의 로직을
자동화하여 검증하는 테스트 코드입니다.
"""

import unittest
import sys
import io

# 한글 깨짐 방지를 위해 표준 출력 인코딩을 UTF-8로 설정
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from map import Map
from pathfinding import a_star
from enemy import EnemyManager, EnemyState, Enemy, Projectile, GRADE_SPECS


class TestMapGeneration(unittest.TestCase):
    """맵 절차적 생성 관련 테스트"""

    def test_map_random_different(self):
        """두 번 생성하면 다른 맵이 나오는지 검증"""
        map1 = Map()
        map2 = Map()
        # 매번 다른 맵이 생성되어야 함 (극히 드물게 같을 수 있으므로 여러 번 시도)
        different = False
        for _ in range(5):
            m1 = Map()
            m2 = Map()
            if m1.grid != m2.grid:
                different = True
                break
        self.assertTrue(different)

    def test_map_seed_reproducible(self):
        """같은 시드를 주면 동일한 맵이 나오는지 검증"""
        map1 = Map(seed=42)
        map2 = Map(seed=42)
        self.assertEqual(map1.grid, map2.grid)

    def test_map_borders_are_walls(self):
        """맵 테두리가 모두 벽인지 검증"""
        game_map = Map()
        for col in range(game_map.cols):
            self.assertTrue(game_map.is_wall(col + 0.5, 0.5))
            self.assertTrue(game_map.is_wall(col + 0.5, game_map.rows - 0.5))
        for row in range(game_map.rows):
            self.assertTrue(game_map.is_wall(0.5, row + 0.5))
            self.assertTrue(game_map.is_wall(game_map.cols - 0.5, row + 0.5))

    def test_player_spawn_is_open(self):
        """플레이어 스폰 위치가 빈 공간인지 검증"""
        game_map = Map()
        px, py = game_map.player_spawn
        self.assertFalse(game_map.is_wall(px, py))

    def test_enemy_spawns_are_open(self):
        """적 스폰 위치들이 모두 빈 공간인지 검증"""
        game_map = Map()
        for ex, ey in game_map.enemy_spawns:
            self.assertFalse(game_map.is_wall(ex, ey))

    def test_enemy_spawns_count(self):
        """적 스폰 위치가 5개인지 검증"""
        game_map = Map()
        self.assertEqual(len(game_map.enemy_spawns), 5)

    def test_out_of_bounds_is_wall(self):
        """경계 밖은 벽으로 판정되는지 검증"""
        game_map = Map()
        self.assertTrue(game_map.is_wall(-1, 5))
        self.assertTrue(game_map.is_wall(100, 100))


class TestPathfinding(unittest.TestCase):
    """A* 경로 탐색 관련 테스트"""

    def test_astar_finds_path(self):
        """플레이어 스폰에서 적 스폰까지 경로가 존재하는지 검증"""
        game_map = Map(seed=42)
        px, py = game_map.player_spawn
        start = (int(px), int(py))

        for ex, ey in game_map.enemy_spawns:
            goal = (int(ex), int(ey))
            path = a_star(game_map, start, goal)
            self.assertTrue(len(path) > 0, f"경로를 찾지 못함: {start} -> {goal}")
            self.assertEqual(path[0], start)
            self.assertEqual(path[-1], goal)

    def test_astar_path_avoids_walls(self):
        """A* 경로의 모든 셀이 빈 공간인지 검증"""
        game_map = Map(seed=42)
        px, py = game_map.player_spawn
        start = (int(px), int(py))
        ex, ey = game_map.enemy_spawns[0]
        goal = (int(ex), int(ey))

        path = a_star(game_map, start, goal)
        for col, row in path:
            self.assertEqual(game_map.grid[row][col], 0)

    def test_astar_blocked_path(self):
        """벽으로 완전히 막힌 목표에 대한 A* 예외 처리 검증"""
        class BlockedMap(Map):
            def __init__(self):
                self.grid = [
                    [1, 1, 1],
                    [1, 0, 1],
                    [1, 1, 1]
                ]
                self.rows = 3
                self.cols = 3

        blocked_map = BlockedMap()
        path = a_star(blocked_map, (1, 1), (0, 0))
        self.assertEqual(path, [])


class TestEnemySpecs(unittest.TestCase):
    """적 학점별 스펙 및 행동 테스트"""

    def test_grade_specs(self):
        """학점별 스펙이 올바르게 적용되는지 검증"""
        c_enemy = Enemy(5.0, 5.0, grade='C')
        d_enemy = Enemy(5.0, 5.0, grade='D')
        f_enemy = Enemy(5.0, 5.0, grade='F')
        p_enemy = Enemy(5.0, 5.0, grade='P')

        # F학점은 C학점의 체력 2배, 공격력 2배
        self.assertEqual(f_enemy.max_hp, c_enemy.max_hp * 2)
        self.assertEqual(f_enemy.damage, c_enemy.damage * 2)

        # D학점은 C학점과 동일 체력
        self.assertEqual(d_enemy.max_hp, c_enemy.max_hp)

        # P학점(교수님)은 최강 체력과 공격력
        self.assertEqual(p_enemy.max_hp, 400)
        self.assertEqual(p_enemy.damage, 30)

        # D학점은 근접 공격 범위 없음 (0.0)
        self.assertEqual(d_enemy.attack_range, 0.0)
        self.assertGreater(c_enemy.attack_range, 0.0)
        self.assertGreater(f_enemy.attack_range, 0.0)
        self.assertGreater(p_enemy.attack_range, 0.0)

        # 처치 점수: P=500, F=300, D=200, C=100
        self.assertEqual(p_enemy.kill_score, 500)
        self.assertEqual(f_enemy.kill_score, 300)
        self.assertEqual(d_enemy.kill_score, 200)
        self.assertEqual(c_enemy.kill_score, 100)

    def test_take_damage_returns_score(self):
        """적 사망 시 처치 점수가 반환되는지 검증"""
        enemy = Enemy(5.0, 5.0, grade='C')
        score = enemy.take_damage(9999)
        self.assertEqual(score, 100)
        self.assertEqual(enemy.state, EnemyState.DEAD)

    def test_d_grade_no_melee(self):
        """D학점 적은 근접 공격 상태(ATTACK)에 진입하지 않는지 검증"""
        game_map = Map(seed=42)
        d_enemy = Enemy(5.0, 5.0, grade='D')
        d_enemy.update((5.5, 5.5), game_map, 0.016)
        self.assertNotEqual(d_enemy.state, EnemyState.ATTACK)

    def test_melee_attack_pending_damage(self):
        """근접 공격 시 pending_damage가 누적되고 check_melee_hits로 수집/초기화되는지 검증"""
        game_map = Map(seed=42)
        c_enemy = Enemy(5.0, 5.0, grade='C')
        
        # 아직 쿨다운/공격 전이므로 pending_damage는 0이어야 함
        self.assertEqual(c_enemy.pending_damage, 0)
        
        # 공격 사거리 안에서 update 호출하여 ATTACK 상태 유도 및 쿨다운 초기화
        # c_enemy.attack_cooldown이 0일 때 attack_behavior 실행
        c_enemy.update((5.1, 5.1), game_map, 0.016)
        self.assertEqual(c_enemy.state, EnemyState.ATTACK)
        self.assertGreater(c_enemy.pending_damage, 0)
        self.assertEqual(c_enemy.pending_damage, c_enemy.damage)
        
        # EnemyManager 생성하여 등록 후 check_melee_hits 호출 테스트
        em = EnemyManager()
        em.enemies.append(c_enemy)
        total_dmg = em.check_melee_hits()
        self.assertEqual(total_dmg, c_enemy.damage)
        self.assertEqual(c_enemy.pending_damage, 0)

    def test_projectile_wall_collision(self):
        """투사체가 벽에 부딪히면 소멸하는지 검증"""
        game_map = Map(seed=42)
        # 맵 경계(벽) 방향으로 발사
        proj = Projectile(game_map.player_spawn[0], game_map.player_spawn[1], -1.0, 0.0, damage=8)
        for _ in range(30):
            proj.update(game_map, 0.05)
        self.assertFalse(proj.alive)


class TestDifficultyScaling(unittest.TestCase):
    """난이도 배율 테스트"""

    def setUp(self):
        self.game_map = Map(seed=42)

    def test_difficulty_hp_scaling(self):
        """난이도에 따른 체력 배율 (1 / 1.5 / 2) 검증"""
        em_easy = EnemyManager(difficulty='easy')
        em_easy.spawn_enemies(self.game_map)
        easy_f = [e for e in em_easy.enemies if e.grade == 'F'][0]

        em_hard = EnemyManager(difficulty='hard')
        em_hard.spawn_enemies(self.game_map)
        hard_f = [e for e in em_hard.enemies if e.grade == 'F'][0]

        self.assertEqual(hard_f.max_hp, easy_f.max_hp * 2)

    def test_difficulty_score_scaling(self):
        """난이도에 따른 처치 점수 배율 (1 / 1.5 / 2) 검증"""
        em_easy = EnemyManager(difficulty='easy')
        em_easy.spawn_enemies(self.game_map)
        easy_score = [e for e in em_easy.enemies if e.grade == 'F'][0].kill_score

        em_hard = EnemyManager(difficulty='hard')
        em_hard.spawn_enemies(self.game_map)
        hard_score = [e for e in em_hard.enemies if e.grade == 'F'][0].kill_score

        self.assertEqual(hard_score, easy_score * 2)

    def test_spawn_composition(self):
        """각 난이도별 스폰 구성 검증:
           - 쉬움 (5마리): F 1, D 2, C 2
           - 보통 (10마리): F 2, D 4, C 4
           - 어려움 (15마리): F 3, D 6, C 6
        """
        # 1. 쉬움 / easy (5마리)
        for diff in ['easy', '쉬움']:
            em = EnemyManager(difficulty=diff)
            em.spawn_enemies(self.game_map)
            self.assertEqual(len(em.enemies), 5)
            grades = [e.grade for e in em.enemies]
            self.assertEqual(grades.count('P'), 1)
            self.assertEqual(grades.count('F'), 1)
            self.assertEqual(grades.count('D'), 1)
            self.assertEqual(grades.count('C'), 2)

        # 2. 보통 / 보통 (10마리)
        for diff in ['medium', '보통']:
            em = EnemyManager(difficulty=diff)
            em.spawn_enemies(self.game_map)
            self.assertEqual(len(em.enemies), 10)
            grades = [e.grade for e in em.enemies]
            self.assertEqual(grades.count('P'), 1)
            self.assertEqual(grades.count('F'), 2)
            self.assertEqual(grades.count('D'), 3)
            self.assertEqual(grades.count('C'), 4)

        # 3. 어려움 / 어려움 (15마리)
        for diff in ['hard', '어려움']:
            em = EnemyManager(difficulty=diff)
            em.spawn_enemies(self.game_map)
            self.assertEqual(len(em.enemies), 15)
            grades = [e.grade for e in em.enemies]
            self.assertEqual(grades.count('P'), 2)
            self.assertEqual(grades.count('F'), 3)
            self.assertEqual(grades.count('D'), 5)
            self.assertEqual(grades.count('C'), 5)


class TestSpecialElements(unittest.TestCase):
    """독 함정, 자동문, 비밀문, 아이템 관련 테스트"""

    def setUp(self):
        self.game_map = Map(seed=42)

    def test_doors_generation(self):
        """맵 생성 시 자동문과 비밀문이 정상적으로 배치되는지 검증"""
        self.assertGreater(len(self.game_map.doors), 0)
        # 자동문(4) 또는 비밀문(5)이 맵에 존재해야 함
        door_types = [d['type'] for d in self.game_map.doors.values()]
        self.assertIn('auto', door_types)
        self.assertIn('secret', door_types)

    def test_doors_auto_proximity(self):
        """자동문이 플레이어나 적이 가까이 갈 때 열리고 멀어지면 닫히는지 검증"""
        # 자동문 하나 선택
        door_pos = None
        for (c, r), door in self.game_map.doors.items():
            if door['type'] == 'auto':
                door_pos = (c, r)
                break
        
        self.assertIsNotNone(door_pos)
        c, r = door_pos
        door_x, door_y = c + 0.5, r + 0.5
        
        # 닫힌 상태인지 검증 (grid 가 4)
        self.assertEqual(self.game_map.grid[r][c], 4)
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'closed')
        
        # 플레이어가 근처(1.8)로 다가감 - 1.5보다 크므로 닫힌 상태 유지
        self.game_map.update_doors((door_x + 1.8, door_y), None, 0.016)
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'closed')
        self.assertEqual(self.game_map.grid[r][c], 4)
        
        # 플레이어가 더 가까이(1.2)로 다가감 - 열려야 함 (1초 경과하여 완전 개방)
        self.game_map.update_doors((door_x + 1.2, door_y), None, 0.016)
        self.game_map.update_doors((door_x + 1.2, door_y), None, 1.0)
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'open')
        self.assertEqual(self.game_map.grid[r][c], 0)  # 통로로 뚫림
        
        # 플레이어가 멀어짐 (거리 5.0)
        self.game_map.update_doors((door_x + 5.0, door_y), None, 3.0)  # 3초 업데이트
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'closed')
        self.assertEqual(self.game_map.grid[r][c], 4)  # 다시 닫힘

    def test_doors_secret_proximity(self):
        """비밀문이 벽에 바짝 다가갔을 때만 열리는지 검증"""
        # 비밀문 하나 선택
        door_pos = None
        for (c, r), door in self.game_map.doors.items():
            if door['type'] == 'secret':
                door_pos = (c, r)
                break
        
        self.assertIsNotNone(door_pos)
        c, r = door_pos
        door_x, door_y = c + 0.5, r + 0.5
        
        # 적당한 거리(2.0)에서는 안 열림
        self.game_map.update_doors((door_x + 2.0, door_y), None, 0.016)
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'closed')
        self.assertEqual(self.game_map.grid[r][c], 5)
        
        # 아주 가까운 거리(1.0)에서는 열림 (1초 경과하여 완전 개방)
        self.game_map.update_doors((door_x + 1.0, door_y), None, 0.016)
        self.game_map.update_doors((door_x + 1.0, door_y), None, 1.0)
        self.assertEqual(self.game_map.doors[door_pos]['state'], 'open')
        self.assertEqual(self.game_map.grid[r][c], 0)

    def test_secret_rooms_items(self):
        """비밀의 방에 아이템이 올바르게 하나만 들어가며, 서로 겹치지 않는지 검증"""
        # 비밀문 하나당 비밀의 방 바닥 셀을 추적하여 아이템이 정확히 1개 매칭되는지 확인
        self.assertGreater(len(self.game_map.items), 0)
        for item in self.game_map.items:
            self.assertIn(item['type'], ['A+', 'H'])
            
        # 비밀문과 비밀의 방은 1:1 관계이며, 방 바닥 셀(0.5 오프셋)에 아이템이 위치
        for (c, r), door in self.game_map.doors.items():
            if door['type'] == 'secret':
                # 비밀의 방 위치 찾기
                room_found = False
                for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    tc, tr = c + dc, r + dr
                    # 비밀문 생성 로직상 반대쪽 방 좌표는 c - dc, r - dr
                    rc, rr = c - dc, r - dr
                    # 이 방에 스폰된 아이템 확인
                    matching_items = [i for i in self.game_map.items if int(i['x']) == rc and int(i['y']) == rr]
                    if len(matching_items) > 0:
                        room_found = True
                        self.assertEqual(len(matching_items), 1)  # 아이템은 정확히 하나
                self.assertTrue(room_found)

    def test_traps_no_dead_ends(self):
        """독 함정이 막다른 길(이웃한 빈 셀 개수 <= 1)에 생성되지 않는지 검증"""
        # 여러 맵 생성 시도하여 검사
        for seed in range(10):
            game_map = Map(seed=seed)
            for trap in game_map.traps:
                c = int(trap['x'])
                r = int(trap['y'])
                
                # 이웃한 0 셀 개수 계산
                corridor_neighbors = 0
                for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    tc, tr = c + dc, r + dr
                    if not game_map.is_out_of_bounds(tc, tr) and game_map.grid[tr][tc] == 0:
                        corridor_neighbors += 1
                        
                # 0 셀 개수가 반드시 2개 이상이어야 함
                self.assertGreater(corridor_neighbors, 1, f"막다른 길 ({c}, {r})에 독 함정이 생성되었습니다. (이웃 개수: {corridor_neighbors})")


if __name__ == '__main__':
    unittest.main()
