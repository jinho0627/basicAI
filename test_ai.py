# test_ai.py
"""
B팀 검증용: 유닛 테스트
이 파일은 맵 충돌 감지, A* 알고리즘의 동작, 적 학점별 스펙, 난이도 배율 등의 로직을
자동화하여 검증하는 테스트 코드입니다.
"""

import unittest
from map import Map
from pathfinding import a_star
from enemy import EnemyManager, EnemyState, Enemy, Projectile, GRADE_SPECS

class TestDoomAI(unittest.TestCase):
    def setUp(self):
        self.game_map = Map()
        self.enemy_manager = EnemyManager()

    def test_map_bounds_and_walls(self):
        """맵 경계 및 벽 충돌 기능 검증"""
        # (0, 0)은 벽이어야 함
        self.assertTrue(self.game_map.is_wall(0.5, 0.5))
        
        # (1.5, 1.5)는 플레이어 스폰 위치이며 빈 공간이어야 함
        self.assertFalse(self.game_map.is_wall(1.5, 1.5))
        
        # 경계 밖은 벽으로 판정되어야 함
        self.assertTrue(self.game_map.is_wall(-1, 5))
        self.assertTrue(self.game_map.is_wall(100, 100))

    def test_astar_pathfinding(self):
        """A* 알고리즘 경로 찾기 동작 검증"""
        start = (1, 1)
        goal = (3, 3)
        path = a_star(self.game_map, start, goal)
        
        self.assertTrue(len(path) > 0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        
        for col, row in path:
            self.assertEqual(self.game_map.grid[row][col], 0)

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

    def test_grade_specs(self):
        """학점별 스펙이 올바르게 적용되는지 검증"""
        c_enemy = Enemy(5.0, 5.0, grade='C')
        d_enemy = Enemy(5.0, 5.0, grade='D')
        f_enemy = Enemy(5.0, 5.0, grade='F')

        # F학점은 C학점의 체력 2배, 공격력 2배
        self.assertEqual(f_enemy.max_hp, c_enemy.max_hp * 2)
        self.assertEqual(f_enemy.damage, c_enemy.damage * 2)

        # D학점은 C학점과 동일 체력
        self.assertEqual(d_enemy.max_hp, c_enemy.max_hp)

        # D학점은 근접 공격 범위 없음 (0.0)
        self.assertEqual(d_enemy.attack_range, 0.0)
        self.assertGreater(c_enemy.attack_range, 0.0)
        self.assertGreater(f_enemy.attack_range, 0.0)

        # 처치 점수: F=300, D=200, C=100
        self.assertEqual(f_enemy.kill_score, 300)
        self.assertEqual(d_enemy.kill_score, 200)
        self.assertEqual(c_enemy.kill_score, 100)

    def test_difficulty_hp_scaling(self):
        """난이도에 따른 체력 배율 (1 / 1.5 / 2) 검증"""
        # Easy (배율 1.0)
        self.enemy_manager.set_difficulty('easy')
        self.enemy_manager.spawn_enemies(self.game_map)
        easy_f = [e for e in self.enemy_manager.enemies if e.grade == 'F'][0]
        easy_c = [e for e in self.enemy_manager.enemies if e.grade == 'C'][0]

        # Hard (배율 2.0)
        self.enemy_manager.set_difficulty('hard')
        self.enemy_manager.spawn_enemies(self.game_map)
        hard_f = [e for e in self.enemy_manager.enemies if e.grade == 'F'][0]
        hard_c = [e for e in self.enemy_manager.enemies if e.grade == 'C'][0]

        # Hard 체력이 Easy 체력의 2배
        self.assertEqual(hard_f.max_hp, easy_f.max_hp * 2)
        self.assertEqual(hard_c.max_hp, easy_c.max_hp * 2)

    def test_difficulty_score_scaling(self):
        """난이도에 따른 처치 점수 배율 (1 / 1.5 / 2) 검증"""
        self.enemy_manager.set_difficulty('easy')
        self.enemy_manager.spawn_enemies(self.game_map)
        easy_score = [e for e in self.enemy_manager.enemies if e.grade == 'F'][0].kill_score

        self.enemy_manager.set_difficulty('hard')
        self.enemy_manager.spawn_enemies(self.game_map)
        hard_score = [e for e in self.enemy_manager.enemies if e.grade == 'F'][0].kill_score

        # Hard 점수가 Easy의 2배
        self.assertEqual(hard_score, easy_score * 2)

    def test_spawn_composition(self):
        """스폰 구성 검증: F 1마리, D 2마리, C 2마리"""
        self.enemy_manager.spawn_enemies(self.game_map)
        grades = [e.grade for e in self.enemy_manager.enemies]
        self.assertEqual(grades.count('F'), 1)
        self.assertEqual(grades.count('D'), 2)
        self.assertEqual(grades.count('C'), 2)

    def test_take_damage_returns_score(self):
        """적 사망 시 처치 점수가 반환되는지 검증"""
        enemy = Enemy(5.0, 5.0, grade='C')
        # 한 번에 죽이기
        score = enemy.take_damage(9999)
        self.assertEqual(score, 100)
        self.assertEqual(enemy.state, EnemyState.DEAD)

    def test_d_grade_no_melee(self):
        """D학점 적은 근접 공격 상태(ATTACK)에 진입하지 않는지 검증"""
        d_enemy = Enemy(5.0, 5.0, grade='D')
        # 플레이어가 바로 옆에 있어도 ATTACK이 아닌 CHASE여야 함
        d_enemy.update((5.5, 5.5), self.game_map, 0.016)
        self.assertNotEqual(d_enemy.state, EnemyState.ATTACK)

    def test_projectile_wall_collision(self):
        """투사체가 벽에 부딪히면 소멸하는지 검증"""
        # (0.5, 0.5) 방향은 벽
        proj = Projectile(1.5, 1.5, -1.0, 0.0, damage=8)
        for _ in range(20):
            proj.update(self.game_map, 0.05)
        self.assertFalse(proj.alive)

if __name__ == '__main__':
    unittest.main()
