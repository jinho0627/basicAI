"""
A팀: 플레이어 이동 및 시점 회전 (부드러운 버전)
"""

import math
import pygame


class Player:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        
        # 이동 속도
        self.move_speed = 4.5        # 기존 3.5 → 4.5 (더 빠름)
        self.rot_speed = 0.0025      # 기존 0.002 → 0.0025 (더 민감)
        
        # 충돌 반경
        self.radius = 0.3
        
        # ━━━ 부드러운 이동을 위한 속도 벡터 ━━━
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.acceleration = 15.0     # 가속도
        self.deceleration = 12.0     # 감속도
        self.max_speed = 5.0         # 최대 속도
        
        # ━━━ 부드러운 회전 ━━━
        self.target_angle = angle
        self.angle_velocity = 0.0
        self.angle_smoothing = 0.15  # 0~1 (낮을수록 부드러움)
    
    def handle_movement(self, keys, dt, game_map):
        """WASD 이동 (가속/감속 적용)"""
        # 입력 방향 계산
        input_x, input_y = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            input_x += math.cos(self.angle)
            input_y += math.sin(self.angle)
        
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            input_x -= math.cos(self.angle)
            input_y -= math.sin(self.angle)
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_x += math.cos(self.angle - math.pi / 2)
            input_y += math.sin(self.angle - math.pi / 2)
        
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_x += math.cos(self.angle + math.pi / 2)
            input_y += math.sin(self.angle + math.pi / 2)
        
        # 입력 정규화
        magnitude = math.sqrt(input_x**2 + input_y**2)
        if magnitude > 0:
            input_x /= magnitude
            input_y /= magnitude
        
        # ━━━ 가속/감속 ━━━
        if magnitude > 0:
            # 가속
            self.vel_x += input_x * self.acceleration * dt
            self.vel_y += input_y * self.acceleration * dt
        else:
            # 감속 (마찰)
            friction = self.deceleration * dt
            if abs(self.vel_x) > friction:
                self.vel_x -= friction * (1 if self.vel_x > 0 else -1)
            else:
                self.vel_x = 0
            
            if abs(self.vel_y) > friction:
                self.vel_y -= friction * (1 if self.vel_y > 0 else -1)
            else:
                self.vel_y = 0
        
        # 최대 속도 제한
        current_speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if current_speed > self.max_speed:
            self.vel_x = (self.vel_x / current_speed) * self.max_speed
            self.vel_y = (self.vel_y / current_speed) * self.max_speed
        
        # 실제 이동 적용
        new_x = self.x + self.vel_x * dt
        new_y = self.y + self.vel_y * dt
        
        # 충돌 판정 및 슬라이딩
        self._apply_collision(new_x, new_y, game_map)
    
    def _apply_collision(self, new_x, new_y, game_map):
        """벽 충돌을 검사하고 슬라이딩 이동"""
        # X축 이동
        if self._can_move_to(new_x, self.y, game_map):
            self.x = new_x
        else:
            self.vel_x = 0  # 충돌 시 속도 초기화
        
        # Y축 이동
        if self._can_move_to(self.x, new_y, game_map):
            self.y = new_y
        else:
            self.vel_y = 0  # 충돌 시 속도 초기화
    
    def _can_move_to(self, x, y, game_map):
        """이동 가능 여부 체크"""
        r = self.radius
        corners = [
            (x - r, y - r),
            (x + r, y - r),
            (x - r, y + r),
            (x + r, y + r),
        ]
        
        for cx, cy in corners:
            if game_map.is_wall(cx, cy):
                return False
        return True
    
    def handle_rotation(self, mouse_rel_x):
        """부드러운 마우스 회전"""
        # 목표 각도 계산
        angle_delta = mouse_rel_x * self.rot_speed
        self.target_angle += angle_delta
        
        # 목표 각도를 0~2π 범위로 정규화
        self.target_angle %= (2 * math.pi)
        
        # 부드러운 보간 (Lerp)
        angle_diff = self.target_angle - self.angle
        
        # 최단 경로로 회전 (360도 넘어갈 때 처리)
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # 선형 보간
        self.angle += angle_diff * self.angle_smoothing
        self.angle %= (2 * math.pi)
    
    def get_pos(self):
        return (self.x, self.y)
    
    def get_direction(self):
        return (math.cos(self.angle), math.sin(self.angle))
