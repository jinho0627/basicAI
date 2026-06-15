"""
A팀 담당: 레이캐스팅 엔진
DDA 알고리즘을 사용하여 각 화면 열마다 광선을 발사하고
벽까지의 거리와 히트 정보를 계산합니다.
"""

import math


class RayCaster:
    def __init__(self, fov=math.pi / 3, max_depth=20):
        """
        레이캐스터를 초기화합니다.
        
        Parameters:
            fov (float): 시야각 (라디안, 기본값 60도)
            max_depth (int): 최대 레이 탐색 거리
        """
        self.fov = fov
        self.max_depth = max_depth
    
    def cast_rays(self, player_x, player_y, player_angle, num_rays, game_map):
        """
        플레이어 위치에서 num_rays개의 광선을 발사하여 벽 충돌 정보를 수집합니다.
        
        Parameters:
            player_x, player_y (float): 플레이어 위치
            player_angle (float): 플레이어 시점 각도
            num_rays (int): 발사할 광선 개수 (화면 가로 해상도)
            game_map (Map): B팀 Map 객체
            
        Returns:
            list: 각 광선의 히트 정보 딕셔너리 리스트
                  [{'distance': float, 'wall_type': int, 'hit_x': float, 'side': str}, ...]
        """
        rays = []
        
        # 시야각의 절반
        half_fov = self.fov / 2
        
        for ray_idx in range(num_rays):
            # 현재 광선의 각도 계산
            # 화면 중앙(ray_idx == num_rays//2)이 player_angle과 일치
            ray_angle = player_angle - half_fov + (ray_idx / num_rays) * self.fov
            
            # DDA 알고리즘으로 벽 충돌 검사
            hit_info = self._cast_single_ray(player_x, player_y, ray_angle, game_map)
            
            # Fisheye 효과 보정 (코사인 보정)
            angle_diff = ray_angle - player_angle
            hit_info['distance'] *= math.cos(angle_diff)
            
            rays.append(hit_info)
        
        return rays
    
    def _cast_single_ray(self, px, py, angle, game_map):
        """
        단일 광선을 발사하여 벽 충돌 정보를 반환합니다. (DDA 알고리즘)
        
        Parameters:
            px, py (float): 광선 시작 위치
            angle (float): 광선 각도
            game_map (Map): 맵 객체
            
        Returns:
            dict: {'distance': float, 'wall_type': int, 'hit_x': float, 'side': str}
        """
        # 광선 방향 벡터
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        # 현재 그리드 위치
        map_x = int(px)
        map_y = int(py)
        
        # DDA: 다음 그리드 경계까지의 거리
        # dx, dy가 0이면 무한대로 설정
        delta_dist_x = abs(1 / dx) if dx != 0 else 1e30
        delta_dist_y = abs(1 / dy) if dy != 0 else 1e30
        
        # 이동 방향 결정
        if dx < 0:
            step_x = -1
            side_dist_x = (px - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - px) * delta_dist_x
        
        if dy < 0:
            step_y = -1
            side_dist_y = (py - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - py) * delta_dist_y
        
        # DDA 루프
        hit = False
        side = 'NS'  # 'NS' = 남북(수직벽), 'EW' = 동서(수평벽)
        
        for _ in range(self.max_depth):
            # 다음 그리드로 이동
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 'EW'
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 'NS'
            
            # 벽 충돌 검사
            if game_map.is_out_of_bounds(map_x, map_y):
                # 맵 경계는 벽으로 처리
                hit = True
                wall_type = 1
                break
            
            wall_type = game_map.get_wall_type(map_x, map_y)
            if wall_type > 0:
                hit = True
                break
        
        # 거리 계산
        if not hit:
            distance = self.max_depth
            wall_type = 0
            hit_x = 0
        else:
            if side == 'EW':
                distance = (map_x - px + (1 - step_x) / 2) / dx
            else:
                distance = (map_y - py + (1 - step_y) / 2) / dy
            
            # 벽 텍스처 매핑용: 히트 지점의 X 좌표 (0~1)
            if side == 'EW':
                hit_x = py + distance * dy
            else:
                hit_x = px + distance * dx
            hit_x -= math.floor(hit_x)  # 소수점 부분만 추출
        
        return {
            'distance': max(distance, 0.1),  # 0 방지
            'wall_type': wall_type,
            'hit_x': hit_x,
            'side': side
        }
