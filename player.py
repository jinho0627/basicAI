# player.py
"""
A팀/B팀 연동: 3D 플레이어 모듈
이 모듈은 3D 공간 상에서 플레이어의 위치(x, y), 시선 각도(angle), 이동 속도를 관리하며,
벽과의 충돌 판정 및 슬라이딩 처리를 지원합니다.
"""

import math
import pygame

class Player:
    def __init__(self, x, y, angle=0.0):
        # 플레이어의 2D 월드 좌표 (실수)
        self.x = x
        self.y = y
        
        # 플레이어가 바라보는 방향 각도 (라디안)
        self.angle = angle
        
        # 카메라 시야각 설정 (Field of View: 60도 = pi / 3)
        self.fov = math.pi / 3.0
        
        # 이동 및 회전 속도 설정
        self.speed = 3.0           # 초당 타일 이동 속도
        self.rotation_speed = 2.5  # 초당 라디안 회전 속도
        self.radius = 0.2          # 플레이어 충돌 범위 반지름

    def rotate(self, direction, dt):
        """방향키 등을 이용한 수동 회전 (direction: -1은 왼쪽, 1은 오른쪽)"""
        self.angle += direction * self.rotation_speed * dt
        self.angle %= math.tau # 0 ~ 2*pi 범위 유지

    def mouse_rotate(self, rel_x, sensitivity=0.0015):
        """마우스 좌우 이동값(rel_x)을 활용한 마우스 시점 회전"""
        self.angle += rel_x * sensitivity
        self.angle %= math.tau

    def update(self, keys, mouse_rel_x, map_obj, dt):
        """
        매 프레임 플레이어의 입력값을 처리하여 이동 및 시선을 업데이트합니다.
        
        Parameters:
            keys (pygame.key.ScancodeWrapper): 현재 눌린 키보드 상태
            mouse_rel_x (int): 마우스 X축 델타 이동량
            map_obj (Map): map.py의 Map 인스턴스
            dt (float): 델타 타임 (초 단위)
        """
        # 1. 시점 회전 처리
        # 마우스 좌우 움직임 반영
        if mouse_rel_x != 0:
            self.mouse_rotate(mouse_rel_x)
            
        # 키보드 시점 회전 보완 (방향키 Left/Right 또는 Q/E 등)
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.rotate(-1, dt)
        if keys[pygame.K_RIGHT] or keys[pygame.K_e]:
            self.rotate(1, dt)

        # 2. WASD 이동 벡터 계산
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0.0, 0.0
        
        # W, S (전진, 후진)
        if keys[pygame.K_w]:
            dx += cos_a
            dy += sin_a
        if keys[pygame.K_s]:
            dx -= cos_a
            dy -= sin_a
            
        # A, D (좌측 게걸음, 우측 게걸음)
        if keys[pygame.K_a]:
            dx += sin_a
            dy -= cos_a
        if keys[pygame.K_d]:
            dx -= sin_a
            dy += cos_a

        # 3. 이동 및 미끄러짐 충돌 처리
        # 이동 벡터가 존재할 때만 연산
        move_len = math.sqrt(dx**2 + dy**2)
        if move_len > 0:
            # 벡터 정규화 및 프레임 속도 적용
            dx = (dx / move_len) * self.speed * dt
            dy = (dy / move_len) * self.speed * dt
            
            # 벽과의 완충 거리(반지름)를 적용하여 X축, Y축 각각 충돌 체크 및 슬라이딩 처리
            new_x = self.x + dx
            new_y = self.y + dy
            
            # X축 이동 처리 (상하 벽면 충돌 체크)
            x_buffer = self.radius if dx > 0 else -self.radius
            if not map_obj.is_wall(new_x + x_buffer, self.y):
                self.x = new_x
                
            # Y축 이동 처리 (좌우 벽면 충돌 체크)
            y_buffer = self.radius if dy > 0 else -self.radius
            if not map_obj.is_wall(self.x, new_y + y_buffer):
                self.y = new_y
