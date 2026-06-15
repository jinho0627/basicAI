"""
A팀 담당: 플레이어 이동 및 마우스 시점 회전
B팀의 Map 클래스와 연동하여 충돌 판정을 수행합니다.
"""

import math
import pygame


class Player:
    def __init__(self, x, y, angle=0):
        """
        플레이어 캐릭터를 생성합니다.
        
        Parameters:
            x, y (float): 플레이어의 초기 월드 좌표 (B팀 Map.player_spawn 사용)
            angle (float): 초기 시점 각도 (라디안, 0 = 동쪽)
        """
        # 위치 및 방향
        self.x = x
        self.y = y
        self.angle = angle  # 라디안 단위 (0 = 동쪽, π/2 = 북쪽)
        
        # 이동/회전 속도
        self.move_speed = 3.0      # 초당 이동 거리
        self.rot_speed = 0.002     # 마우스 감도 (픽셀당 회전 각도)
        
        # 충돌 판정용 반지름
        self.radius = 0.3
        
        # 체력 (C팀 연동용)
        self.max_hp = 100
        self.hp = self.max_hp
        
    def handle_movement(self, keys, dt, game_map):
        """
        WASD 키 입력을 처리하여 플레이어를 이동시킵니다.
        
        Parameters:
            keys: pygame.key.get_pressed() 결과
            dt (float): 델타 타임 (초 단위)
            game_map (Map): B팀의 Map 인스턴스
        """
        # 방향 벡터 계산
        dx, dy = 0, 0
        
        # W: 전진 (현재 바라보는 방향)
        if keys[pygame.K_w]:
            dx += math.cos(self.angle)
            dy += math.sin(self.angle)
        
        # S: 후진
        if keys[pygame.K_s]:
            dx -= math.cos(self.angle)
            dy -= math.sin(self.angle)
        
        # A: 왼쪽 스트레이프 (각도 - 90도)
        if keys[pygame.K_a]:
            dx += math.cos(self.angle - math.pi / 2)
            dy += math.sin(self.angle - math.pi / 2)
        
        # D: 오른쪽 스트레이프 (각도 + 90도)
        if keys[pygame.K_d]:
            dx += math.cos(self.angle + math.pi / 2)
            dy += math.sin(self.angle + math.pi / 2)
        
        # 벡터 정규화 (대각선 이동 시 속도 보정)
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
            
            # 실제 이동량 계산
            move_distance = self.move_speed * dt
            new_x = self.x + dx * move_distance
            new_y = self.y + dy * move_distance
            
            # 충돌 판정 및 슬라이딩
            self._apply_collision(new_x, new_y, game_map)
    
    def _apply_collision(self, new_x, new_y, game_map):
        """
        벽 충돌을 검사하고 슬라이딩 이동을 적용합니다.
        
        Parameters:
            new_x, new_y (float): 이동하려는 새로운 좌표
            game_map (Map): 맵 객체
        """
        # X축만 이동 시도 (Y 고정)
        if self._can_move_to(new_x, self.y, game_map):
            self.x = new_x
        
        # Y축만 이동 시도 (X 고정)
        if self._can_move_to(self.x, new_y, game_map):
            self.y = new_y
    
    def _can_move_to(self, x, y, game_map):
        """
        특정 좌표로 이동 가능한지 검사합니다.
        플레이어의 반지름을 고려하여 4개 모서리를 검사합니다.
        
        Parameters:
            x, y (float): 검사할 좌표
            game_map (Map): 맵 객체
            
        Returns:
            bool: 이동 가능 여부
        """
        # 플레이어 몸체의 4개 모서리 검사
        r = self.radius
        corners = [
            (x - r, y - r),  # 좌상단
            (x + r, y - r),  # 우상단
            (x - r, y + r),  # 좌하단
            (x + r, y + r),  # 우하단
        ]
        
        for cx, cy in corners:
            if game_map.is_wall(cx, cy):
                return False
        
        return True
    
    def handle_rotation(self, mouse_rel_x):
        """
        마우스 좌우 이동으로 시점을 회전시킵니다.
        
        Parameters:
            mouse_rel_x (int): 마우스 상대 이동량 X축
        """
        self.angle += mouse_rel_x * self.rot_speed
        
        # 각도를 0 ~ 2π 범위로 정규화
        self.angle %= (2 * math.pi)
    
    def get_direction_vector(self):
        """
        현재 바라보는 방향의 단위 벡터를 반환합니다.
        
        Returns:
            tuple: (dx, dy) 방향 벡터
        """
        return (math.cos(self.angle), math.sin(self.angle))
    
    def get_pos(self):
        """플레이어의 현재 위치를 반환합니다."""
        return (self.x, self.y)
    
    def take_damage(self, amount):
        """
        플레이어가 피해를 입습니다. (C팀/B팀 연동)
        
        Parameters:
            amount (int): 피해량
            
        Returns:
            bool: 사망 여부 (True면 사망)
        """
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0
    
    def heal(self, amount):
        """체력을 회복합니다."""
        self.hp = min(self.max_hp, self.hp + amount)
