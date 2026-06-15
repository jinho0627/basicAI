"""
A팀 담당: FPS 화면 렌더링
레이캐스팅 결과를 바탕으로 3D 원근감 있는 화면을 그립니다.
"""

import pygame
import math


class Renderer:
    def __init__(self, screen_width, screen_height):
        """
        렌더러를 초기화합니다.
        
        Parameters:
            screen_width, screen_height (int): 화면 해상도
        """
        self.width = screen_width
        self.height = screen_height
        self.half_height = screen_height // 2
        
        # 색상 정의
        self.ceiling_color = (50, 50, 50)
        self.floor_color = (100, 100, 100)
        
        # 벽 타입별 색상 (B팀 맵의 wall_type에 따라)
        self.wall_colors = {
            1: (200, 200, 200),  # 기본 벽
            2: (150, 150, 200),  # 파란 벽
            3: (200, 150, 150),  # 붉은 벽
        }
    
    def render_frame(self, screen, rays, enemies=None, projectiles=None):
        """
        한 프레임을 렌더링합니다.
        
        Parameters:
            screen: Pygame 화면 객체
            rays (list): RayCaster.cast_rays() 결과
            enemies (list): B팀 Enemy 객체 리스트 (옵션)
            projectiles (list): B팀 Projectile 객체 리스트 (옵션)
        """
        # 1. 천장과 바닥 그리기
        screen.fill(self.ceiling_color, (0, 0, self.width, self.half_height))
        screen.fill(self.floor_color, (0, self.half_height, self.width, self.half_height))
        
        # 2. 벽 렌더링
        num_rays = len(rays)
        column_width = self.width / num_rays
        
        for i, ray in enumerate(rays):
            self._render_wall_slice(screen, i, column_width, ray)
        
        # 3. 적 렌더링 (옵션, 나중에 구현)
        # TODO: 적과 투사체는 추후 스프라이트 렌더링으로 추가
    
    def _render_wall_slice(self, screen, column_idx, column_width, ray):
        """
        한 개의 수직 벽 슬라이스를 렌더링합니다.
        
        Parameters:
            screen: Pygame 화면
            column_idx (int): 열 인덱스
            column_width (float): 한 열의 가로 폭
            ray (dict): 광선 정보
        """
        distance = ray['distance']
        wall_type = ray['wall_type']
        side = ray['side']
        
        if wall_type == 0:
            return  # 벽이 없으면 그리지 않음
        
        # 벽 높이 계산 (거리에 반비례)
        wall_height = int(self.height / distance)
        
        # 벽의 그리기 시작/끝 위치
        draw_start = max(0, self.half_height - wall_height // 2)
        draw_end = min(self.height, self.half_height + wall_height // 2)
        
        # 색상 선택
        base_color = self.wall_colors.get(wall_type, (200, 200, 200))
        
        # 면에 따라 명암 적용 (동서벽을 더 어둡게)
        if side == 'EW':
            color = tuple(int(c * 0.7) for c in base_color)
        else:
            color = base_color
        
        # 거리에 따른 어두워짐 효과 (옵션)
        fog_factor = max(0.3, 1.0 - distance / 15.0)
        color = tuple(int(c * fog_factor) for c in color)
        
        # 벽 슬라이스 그리기
        x = int(column_idx * column_width)
        width = max(1, int(column_width + 1))  # 틈새 방지
        
        pygame.draw.rect(
            screen,
            color,
            (x, draw_start, width, draw_end - draw_start)
        )
