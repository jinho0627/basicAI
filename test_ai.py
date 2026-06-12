# test_ai.py
"""
B팀 검증용: 유닛 테스트
이 파일은 맵 충돌 감지, A* 알고리즘의 동작, 적 난이도 속성 변경 등의 로직을
자동화하여 검증하는 테스트 코드입니다.
"""

import unittest
from map import Map
from pathfinding import a_star
from enemy import EnemyManager, EnemyState, Enemy

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
        # 플레이어 스폰(1, 1)에서 첫 번째 스폰지점(3, 3)으로의 경로 탐색
        start = (1, 1)
        goal = (3, 3)
        path = a_star(self.game_map, start, goal)
        
        # 경로가 존재해야 함
        self.assertTrue(len(path) > 0)
        # 경로의 시작점은 start여야 함
        self.assertEqual(path[0], start)
        # 경로의 끝점은 goal이어야 함
        self.assertEqual(path[-1], goal)
        
        # 경로 상의 모든 셀이 벽이 아니어야 함
        for col, row in path:
            self.assertEqual(self.game_map.grid[row][col], 0)

    def test_astar_blocked_path(self):
        """벽으로 완전히 막힌 목표에 대한 A* 예외 처리 검증"""
        # 인위적으로 완전히 격리된 맵 생성
        # 3x3 맵에서 (1, 1)이 빈 공간이고 주변이 다 벽
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
        # 벽인 (0, 0)으로 가는 경로 검색 -> 빈 리스트여야 함
        path = a_star(blocked_map, (1, 1), (0, 0))
        self.assertEqual(path, [])

    def test_difficulty_scaling(self):
        """난이도 조절이 적의 스펙에 정상적으로 미치는지 검증"""
        # Easy 난이도로 적 스폰
        self.enemy_manager.set_difficulty('easy')
        self.enemy_manager.spawn_enemies(self.game_map)
        
        easy_enemy = self.enemy_manager.enemies[0]
        easy_hp = easy_enemy.max_hp
        easy_speed = easy_enemy.speed
        
        # Hard 난이도로 변경
        self.enemy_manager.set_difficulty('hard')
        hard_enemy = self.enemy_manager.enemies[0]
        hard_hp = hard_enemy.max_hp
        hard_speed = hard_enemy.speed
        
        # Hard 난이도의 체력과 속도가 Easy 난이도보다 높아야 함
        self.assertTrue(hard_hp > easy_hp)
        self.assertTrue(hard_speed > easy_speed)

if __name__ == '__main__':
    unittest.main()
