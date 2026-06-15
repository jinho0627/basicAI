"""
A팀: 레이캐스팅 엔진 
"""

import math


class RayCaster:
    def __init__(self, fov=math.pi / 2.5, max_depth=25):  # FOV 60도 → 72도
        """
        Parameters:
            fov: 시야각 증가 (더 넓은 시야)
            max_depth: 최대 탐색 거리 증가
        """
        self.fov = fov
        self.max_depth = max_depth
    
    def cast_rays(self, player_x, player_y, player_angle, num_rays, game_map):
        """광선 발사 (화면 해상도만큼)"""
        rays = []
        half_fov = self.fov / 2
        
        for ray_idx in range(num_rays):
            # 각 픽셀마다 정확히 하나의 광선
            ray_angle = player_angle - half_fov + (ray_idx / num_rays) * self.fov
            hit_info = self._cast_single_ray(player_x, player_y, ray_angle, game_map)
            
            # Fisheye 보정
            angle_diff = ray_angle - player_angle
            hit_info['distance'] *= math.cos(angle_diff)
            
            rays.append(hit_info)
        
        return rays
    
    def _cast_single_ray(self, px, py, angle, game_map):
        """DDA 알고리즘 (동일)"""
        dx = math.cos(angle)
        dy = math.sin(angle)
        
        map_x = int(px)
        map_y = int(py)
        
        delta_dist_x = abs(1 / dx) if dx != 0 else 1e30
        delta_dist_y = abs(1 / dy) if dy != 0 else 1e30
        
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
        
        hit = False
        side = 'NS'
        
        for _ in range(int(self.max_depth * 2)):
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 'EW'
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 'NS'
            
            if game_map.is_out_of_bounds(map_x, map_y):
                hit = True
                wall_type = 1
                break
            
            wall_type = game_map.get_wall_type(map_x, map_y)
            if wall_type > 0:
                hit = True
                break
        
        if not hit:
            distance = self.max_depth
            wall_type = 0
            hit_x = 0
        else:
            if side == 'EW':
                distance = (map_x - px + (1 - step_x) / 2) / dx
            else:
                distance = (map_y - py + (1 - step_y) / 2) / dy
            
            if side == 'EW':
                hit_x = py + distance * dy
            else:
                hit_x = px + distance * dx
            hit_x -= math.floor(hit_x)
        
        return {
            'distance': max(distance, 0.1),
            'wall_type': wall_type,
            'hit_x': hit_x,
            'side': side
        }
