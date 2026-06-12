# raycasting.py
"""
A팀 담당: 3D 레이캐스팅(Raycasting) 엔진 모듈
이 모듈은 DDA(Digital Differential Analysis) 알고리즘을 사용해 광선(Ray)을 쏘아 벽과의 거리를 연산하고,
이를 기반으로 3D 미로 화면을 원근감 있게 그립니다.
또한 적 캐릭터 렌더링을 위해 깊이 버퍼(Depth Buffer / Z-Buffer)를 생성합니다.
"""

import math
import pygame

# 3D 렌더링을 위한 화면 상수
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
HALF_HEIGHT = SCREEN_HEIGHT // 2

# 광선 주사율 최적화 (성능과 화질 타협점)
NUM_RAYS = 160                 # 화면 가로 크기 대비 주사할 레이 개수 (부드러운 화면을 위한 해상도 설정)
SCALE = SCREEN_WIDTH // NUM_RAYS # 각 레이가 그릴 화면 열의 픽셀 폭

# 거리 계수 (벽 높이 조절)
DIST_COEFF = 2.5 * 160  # 벽의 크기 배율

# 거리 감쇠 안개(Fog) 색상
FOG_COLOR = (15, 15, 20)

def raycast(screen, player, map_obj):
    """
    DDA 알고리즘을 이용해 광선을 쏘고 3D 벽면을 렌더링합니다.
    적 스프라이트 정렬 및 깊이 가림 처리를 위한 depth_buffer 리스트를 반환합니다.
    """
    depth_buffer = [float('inf')] * NUM_RAYS
    
    # 1. 천장과 바닥 채우기 (화면을 반으로 나누어 천장은 짙은 회색, 바닥은 어두운 녹갈색)
    # 천장 (Ceiling)
    pygame.draw.rect(screen, (30, 30, 35), (0, 0, SCREEN_WIDTH, HALF_HEIGHT))
    # 바닥 (Floor)
    pygame.draw.rect(screen, (40, 40, 45), (0, HALF_HEIGHT, SCREEN_WIDTH, HALF_HEIGHT))

    # 2. 각 레이(Ray)별로 3D 계산 진행
    start_angle = player.angle - (player.fov / 2.0)
    angle_step = player.fov / NUM_RAYS

    for i in range(NUM_RAYS):
        ray_angle = start_angle + i * angle_step
        sin_a = math.sin(ray_angle) if math.sin(ray_angle) != 0 else 1e-6
        cos_a = math.cos(ray_angle) if math.cos(ray_angle) != 0 else 1e-6

        # 플레이어가 위치한 그리드 좌표
        map_x, map_y = int(player.x), int(player.y)

        # DDA 알고리즘을 위한 격자별 거리 증가값 계산
        delta_dist_x = abs(1.0 / cos_a)
        delta_dist_y = abs(1.0 / sin_a)

        # 광선의 진행 방향에 따른 초기 격자 오프셋 및 탐색 방향 설정
        if cos_a < 0:
            step_x = -1
            side_dist_x = (player.x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player.x) * delta_dist_x

        if sin_a < 0:
            step_y = -1
            side_dist_y = (player.y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player.y) * delta_dist_y

        # DDA 루프 실행 - 벽을 만날 때까지 격자 단위 전진
        hit = False
        side = 0 # 0: X축 정렬 벽면 충돌, 1: Y축 정렬 벽면 충돌
        wall_type = 1
        
        # 무한 루프 방지용 최대 사거리
        max_depth = 20
        depth = 0.0

        while not hit and depth < max_depth:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                
            # 맵 충돌 체크
            if map_obj.is_out_of_bounds(map_x, map_y):
                break
                
            tile_val = map_obj.grid[map_y][map_x]
            if tile_val > 0:
                hit = True
                wall_type = tile_val

        # 3. 벽까지의 정확한 최단 거리(투영 거리) 계산
        if side == 0:
            distance = (map_x - player.x + (1.0 - step_x) / 2.0) / cos_a
        else:
            distance = (map_y - player.y + (1.0 - step_y) / 2.0) / sin_a

        # 어색한 뒤틀림 방지: 벽면 거리가 너무 좁은 경우 예외 처리
        if distance < 0.01:
            distance = 0.01

        # 4. 어안 렌즈 효과(Fish-eye distortion) 코사인 보정
        corrected_dist = distance * math.cos(ray_angle - player.angle)
        
        # 깊이 버퍼 기록 (적 렌더링에 사용)
        depth_buffer[i] = corrected_dist

        # 5. 거리에 기반한 벽 높이 계산
        wall_height = int(DIST_COEFF / (corrected_dist if corrected_dist > 0.01 else 0.01))
        # 화면 경계를 넘어가는 오버플로우 방지
        wall_height = min(wall_height, SCREEN_HEIGHT * 4)

        # 6. 벽면 명암 및 텍스처 스타일 렌더링
        # 벽 종류별 기본 색상 매핑
        if wall_type == 1:
            base_color = (130, 140, 160)  # 일반 회색 벽
        elif wall_type == 2:
            base_color = (180, 80, 80)    # 붉은 벽돌 벽
        elif wall_type == 3:
            base_color = (60, 140, 80)    # 이끼 낀 녹색 벽
        else:
            base_color = (120, 120, 120)

        # Y축 벽면은 그림자가 지도록 색상을 약간 어둡게 (3D 입체 명암)
        if side == 1:
            r, g, b = base_color
            base_color = (int(r * 0.7), int(g * 0.7), int(b * 0.7))

        # 거리 감쇠 효과 (Distance Fog) 적용: 멀어질수록 안개색(어두운 색)에 가까워짐
        fog_factor = 1.0 / (1.0 + corrected_dist * corrected_dist * 0.05)
        # 안개 최소 비율 제한
        fog_factor = max(0.0, min(1.0, fog_factor))
        
        final_color = (
            int(base_color[0] * fog_factor + FOG_COLOR[0] * (1.0 - fog_factor)),
            int(base_color[1] * fog_factor + FOG_COLOR[1] * (1.0 - fog_factor)),
            int(base_color[2] * fog_factor + FOG_COLOR[2] * (1.0 - fog_factor))
        )

        # 7. 기하학적 벽 드로잉
        # 수직선의 시작/끝 픽셀 좌표
        draw_start = HALF_HEIGHT - wall_height // 2
        draw_start = max(0, draw_start)
        draw_end = HALF_HEIGHT + wall_height // 2
        draw_end = min(SCREEN_HEIGHT, draw_end)

        # 수직 바(Bar) 그리기 (열 너비는 SCALE 값)
        pygame.draw.rect(
            screen,
            final_color,
            (i * SCALE, draw_start, SCALE, draw_end - draw_start)
        )

    return depth_buffer
