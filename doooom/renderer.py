"""
A팀: 3D 렌더링
"""

import pygame
import math


class Renderer:
    def __init__(self, screen_width, screen_height, hud_height=80):
        self.width = screen_width
        self.total_height = screen_height
        self.hud_height = hud_height
        self.game_height = screen_height - hud_height
        self.half_height = self.game_height // 2
        
        # 색상 (더 풍부한 톤)
        self.ceiling_color = (30, 25, 35)    # 어두운 보라
        self.floor_color = (45, 40, 35)      # 어두운 갈색
        
        # 벽 색상 (더 선명)
        self.wall_colors = {
            1: (180, 140, 120),  # 따뜻한 돌벽
            2: (120, 120, 160),  # 푸른 벽
            3: (160, 100, 100),  # 붉은 벽
        }
        
        # ━━━ 부드러운 렌더링 ━━━
        self.fog_distance = 20.0      # 안개 거리
        self.min_brightness = 0.15    # 최소 밝기
    
    def render_frame(self, screen, rays, enemies=None, projectiles=None):
        """3D 화면 렌더링"""
        # 천장과 바닥 (그라디언트 효과)
        self._render_floor_ceiling(screen)
        
        # 벽 렌더링
        num_rays = len(rays)
        column_width = self.width / num_rays
        
        for i, ray in enumerate(rays):
            self._render_wall_slice(screen, i, column_width, ray)
    
    def _render_floor_ceiling(self, screen):
        """천장/바닥 그라디언트"""
        # 천장
        for y in range(self.half_height):
            ratio = y / self.half_height
            color = tuple(int(c * (0.5 + ratio * 0.5)) for c in self.ceiling_color)
            pygame.draw.line(screen, color, (0, y), (self.width, y))
        
        # 바닥
        for y in range(self.half_height, self.game_height):
            ratio = (y - self.half_height) / self.half_height
            color = tuple(int(c * (1.0 - ratio * 0.3)) for c in self.floor_color)
            pygame.draw.line(screen, color, (0, y), (self.width, y))
    
    def _render_wall_slice(self, screen, column_idx, column_width, ray):
        """벽 한 줄 그리기 (부드러운 음영)"""
        distance = ray['distance']
        wall_type = ray['wall_type']
        side = ray['side']
        
        if wall_type == 0:
            return
        
        # 벽 높이 계산
        wall_height = int(self.game_height / (distance + 0.0001))
        
        draw_start = max(0, self.half_height - wall_height // 2)
        draw_end = min(self.game_height, self.half_height + wall_height // 2)
        
        # 기본 색상
        base_color = self.wall_colors.get(wall_type, (180, 140, 120))
        
        # 면별 명암 (EW 벽 더 어둡게)
        if side == 'EW':
            color = tuple(int(c * 0.75) for c in base_color)
        else:
            color = base_color
        
        # ━━━ 부드러운 거리 기반 밝기 ━━━
        fog_factor = 1.0 - min(distance / self.fog_distance, 1.0)
        fog_factor = max(fog_factor, self.min_brightness)
        
        # 비선형 감쇠 (더 자연스러움)
        fog_factor = fog_factor ** 0.7
        
        color = tuple(int(c * fog_factor) for c in color)
        
        # 그리기 (안티앨리어싱 효과)
        x = int(column_idx * column_width)
        width = max(1, int(column_width + 1))
        
        # 벽 메인
        pygame.draw.rect(
            screen,
            color,
            (x, draw_start, width, draw_end - draw_start)
        )
        
        # ━━━ 부드러운 테두리 효과 (옵션) ━━━
        if width > 1 and distance < 5:
            edge_color = tuple(min(255, int(c * 1.1)) for c in color)
            pygame.draw.line(screen, edge_color, (x, draw_start), (x, draw_end), 1)
