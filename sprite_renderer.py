# sprite_renderer.py
"""
A팀/B팀 연동: 3D 적 스프라이트 렌더러 모듈
이 모듈은 2D 평면 상의 적(Enemy) 위치를 플레이어 시선 기준의 카메라 스페이스로 변환하고,
3D 공간 상에 투영된 적의 크기를 계산하여 렌더링합니다.
레이캐스터가 반환한 depth_buffer를 기반으로 Z-Buffer 처리를 수행하여 벽에 가려진 적은 보이지 않게 처리합니다.
"""

import math
import pygame
from enemy import EnemyState

# raycasting.py의 화면 구성 설정 참조
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
HALF_HEIGHT = SCREEN_HEIGHT // 2
DIST_COEFF = 2.5 * 160  # 벽과 동일한 투영 크기 배율 적용

def render_enemies(screen, player, enemies, depth_buffer):
    """
    모든 적 스프라이트를 3D 화면에 투영하여 렌더링합니다.
    
    Parameters:
        screen (pygame.Surface): 화면 표면
        player (Player): player.py의 Player 인스턴스
        enemies (list): 살아있는 적 객체 리스트
        depth_buffer (list): 레이캐스터가 기록한 각 화면 열의 벽까지의 거리 리스트
    """
    # 1. 플레이어와의 거리에 따라 적들을 정렬합니다 (뒤에 있는 적부터 앞에 있는 적 순으로 그리는 Painters Algorithm)
    def get_distance(enemy):
        return math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
        
    sorted_enemies = sorted(enemies, key=get_distance, reverse=True)
    
    # 3D 레이캐스터의 레이 주사율 계수와 스케일 가져오기
    num_rays = len(depth_buffer)
    scale = SCREEN_WIDTH // num_rays

    for enemy in sorted_enemies:
        if enemy.state == EnemyState.DEAD:
            continue
            
        # 플레이어와 적 사이의 상대적 거리 벡터
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        
        # 2. 플레이어의 시선 각도에 맞춘 카메라 좌표계(Camera Space)로의 변환
        # sprite_y: 플레이어 기준 전방 깊이 (거리)
        # sprite_x: 플레이어 기준 좌우 횡방향 편차
        sin_a = math.sin(player.angle)
        cos_a = math.cos(player.angle)
        
        sprite_x = dx * sin_a - dy * cos_a
        sprite_y = dx * cos_a + dy * sin_a

        # 적이 카메라 뒤에 있거나 시야 밖(너무 가깝거나 너무 먼 경우)이면 렌더링 패스
        if sprite_y <= 0.2:
            continue

        # 3. 3D 투영 크기(높이 및 너비) 계산
        # 거리에 반비례하도록 몬스터 스프라이트 크기 스케일링
        sprite_size = int(DIST_COEFF / sprite_y)
        # 지나치게 큰 크기 제한
        sprite_size = min(sprite_size, SCREEN_HEIGHT * 2)

        # 화면상의 수직 중심선 결정 (천장과 바닥의 경계 부근)
        sprite_screen_y = HALF_HEIGHT - sprite_size // 2

        # 4. 화면상의 수평 중심 위치 결정 (시야각 FOV 기준 카메라 평면 투영)
        # 플레이어 정면을 기준으로 각도를 비율화하여 화면 X 좌표 계산
        fov = player.fov
        sprite_screen_x = int((SCREEN_WIDTH / 2) * (1.0 + sprite_x / (sprite_y * math.tan(fov / 2.0))))

        # 스프라이트의 가로 그리기 시작/끝 영역 계산
        start_x = sprite_screen_x - sprite_size // 2
        end_x = sprite_screen_x + sprite_size // 2
        
        # 화면을 벗어나면 패스
        if start_x >= SCREEN_WIDTH or end_x < 0:
            continue

        # 5. 수직선(Vertical Slice) 단위로 Z-Buffer 검사 및 렌더링
        # 이미지가 없으므로, 수직선 단위로 기하도형(원형 및 눈동자 픽셀 등)을 그려 빌보드 효과를 모방합니다.
        for col_idx in range(start_x, end_x):
            # 화면 컬럼 범위 내에 있는지 확인
            if col_idx < 0 or col_idx >= SCREEN_WIDTH:
                continue
                
            # 레이캐스터의 깊이 버퍼 인덱스 매핑 (SCREEN_WIDTH -> num_rays 변환)
            ray_idx = col_idx // scale
            if ray_idx < 0 or ray_idx >= num_rays:
                continue

            # Z-Buffer 검사: 적이 현재 열의 벽 뒤에 있다면 그리지 않음
            if sprite_y >= depth_buffer[ray_idx]:
                continue

            # 스프라이트 내에서 현재 그리는 수직 컬럼의 로컬 비율 (0.0 ~ 1.0)
            t = (col_idx - start_x) / sprite_size
            
            # 몬스터의 형태를 수학적 픽셀 비율로 조각내서 그립니다.
            # 원형 몸체 범위 안에 해당하는 수직선인지 체크 (r^2 = (t-0.5)^2 + (y-0.5)^2 <= 0.25)
            # 타원형 몸체의 높이를 계산합니다.
            half_w_ratio = t - 0.5
            if abs(half_w_ratio) > 0.5:
                continue
                
            # 타원의 세로 높이 계수
            h_ratio = math.sqrt(max(0.0, 0.25 - half_w_ratio**2)) * 2.0  # 0.0 ~ 1.0 범위
            
            h_slice = int(sprite_size * h_ratio)
            draw_y_start = HALF_HEIGHT - h_slice // 2
            draw_y_end = HALF_HEIGHT + h_slice // 2
            
            # 상태에 따라 기본 몬스터 색상 지정
            if enemy.state == EnemyState.ATTACK:
                base_color = (255, 30, 30)       # 격렬한 빨간색
            elif enemy.state == EnemyState.CHASE:
                base_color = (220, 80, 0)        # 짙은 주황색
            else:
                base_color = (180, 120, 0)       # 순찰 상태는 노란 계열

            # 입체감을 위해 몸체의 가장자리는 어둡게 그라데이션 처리
            shading = math.sin(t * math.pi)  # 중심부일수록 1.0에 수렴
            color = (
                int(base_color[0] * shading),
                int(base_color[1] * shading),
                int(base_color[2] * shading)
            )
            
            # 거리 감쇠 효과 (Fog)를 적 스프라이트에도 동일 적용하여 벽과 위화감 제거
            fog_factor = 1.0 / (1.0 + sprite_y * sprite_y * 0.05)
            fog_factor = max(0.0, min(1.0, fog_factor))
            
            fog_color = (15, 15, 20)
            final_color = (
                int(color[0] * fog_factor + fog_color[0] * (1.0 - fog_factor)),
                int(color[1] * fog_factor + fog_color[1] * (1.0 - fog_factor)),
                int(color[2] * fog_factor + fog_color[2] * (1.0 - fog_factor))
            )

            # 6. 수직 조각(Slice) 그리기
            pygame.draw.line(screen, final_color, (col_idx, draw_y_start), (col_idx, draw_y_end), 1)
            
            # --- 디테일: 몬스터 눈동자 디테일 추가 ---
            # 적이 플레이어 쪽을 쳐다볼 때 눈동자 시각화 (눈 높이는 몸통 중앙 부근, 가로 비율 0.4 ~ 0.6)
            if 0.45 <= t <= 0.55:
                eye_h = int(sprite_size * 0.1)
                # 눈동자 색상: 흰자위와 검은 눈동자 조화
                eye_y_start = HALF_HEIGHT - eye_h // 2
                eye_y_end = HALF_HEIGHT + eye_h // 2
                
                # 외눈박이 몬스터 눈동자
                eye_color = (255, 255, 255) # 기본 흰 눈
                if 0.48 <= t <= 0.52:
                    eye_color = (0, 255, 0) if enemy.state == EnemyState.CHASE else (0, 0, 0) # 검은색 혹은 녹색 안광
                    
                # Fog 적용
                final_eye_color = (
                    int(eye_color[0] * fog_factor + fog_color[0] * (1.0 - fog_factor)),
                    int(eye_color[1] * fog_factor + fog_color[1] * (1.0 - fog_factor)),
                    int(eye_color[2] * fog_factor + fog_color[2] * (1.0 - fog_factor))
                )
                pygame.draw.line(screen, final_eye_color, (col_idx, eye_y_start), (col_idx, eye_y_end), 1)
