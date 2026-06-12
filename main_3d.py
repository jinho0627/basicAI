# main_3d.py
"""
통합 실행 파일: 3D 둠(Doom) 스타일 게임 엔진
이 모듈은 B팀의 맵, A* 경로 탐색, FSM 적 AI에 더해,
A팀의 3D 레이캐스팅 벽면 렌더링 및 C팀의 무기 발사, 체력 HUD 시스템을 통합하여
완벽하게 구동되는 3D 둠 프로토타입 게임을 구현합니다.

조작 방법:
- [W, A, S, D]: 플레이어 이동 (앞, 좌, 뒤, 우)
- [마우스 좌우 이동]: 시점 회전 (마우스 캡처 모드 자동 적용)
- [마우스 좌클릭]: 총기 사격 (화면 중앙 크로스헤어 정밀 조준)
- [키보드 1, 2, 3]: 실시간 난이도 조절 (1: 쉬움, 2: 보통, 3: 어려움)
- [ESC]: 마우스 커서 해제 / 재캡처 (창 클릭 시 재캡처)
- [R]: 사망 혹은 게임 종료 시 재시작
"""

import sys
import math
import pygame
from map import Map
from player import Player
from enemy import EnemyManager, EnemyState
from raycasting import raycast, SCREEN_WIDTH, SCREEN_HEIGHT, HALF_HEIGHT
from sprite_renderer import render_enemies

# HUD 바 높이 설정
HUD_HEIGHT = 80
WINDOW_HEIGHT = SCREEN_HEIGHT + HUD_HEIGHT

# 색상
COLOR_HUD_BG = (25, 25, 30)
COLOR_HUD_BORDER = (45, 45, 55)
COLOR_TEXT = (240, 240, 255)
COLOR_AMMO = (255, 215, 0)
COLOR_HEALTH = (220, 40, 40)

def draw_hud(screen, player_hp, score, difficulty, active_enemies):
    """화면 하단에 둠(Doom) 레트로 스타일의 HUD 바를 렌더링합니다."""
    hud_rect = pygame.Rect(0, SCREEN_HEIGHT, SCREEN_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, COLOR_HUD_BG, hud_rect)
    pygame.draw.line(screen, COLOR_HUD_BORDER, (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), 3)
    
    font = pygame.font.SysFont("malgungothic", 18, bold=True)
    small_font = pygame.font.SysFont("malgungothic", 12, bold=True)

    # 1. 체력 정보 (HEALTH)
    pygame.draw.rect(screen, (50, 10, 10), (25, SCREEN_HEIGHT + 25, 150, 20))
    hp_width = int(150 * (player_hp / 100.0))
    if hp_width > 0:
        pygame.draw.rect(screen, COLOR_HEALTH, (25, SCREEN_HEIGHT + 25, hp_width, 20))
    
    hp_text = font.render(f"HEALTH: {player_hp}%", True, COLOR_TEXT)
    screen.blit(hp_text, (25, SCREEN_HEIGHT + 5))

    # 2. 난이도 및 처치 상황 정보
    diff_text_map = {'easy': 'EASY', 'medium': 'NORMAL', 'hard': 'NIGHTMARE'}
    diff_color_map = {'easy': (0, 200, 255), 'medium': (0, 255, 120), 'hard': (255, 50, 50)}
    diff_str = diff_text_map.get(difficulty, 'NORMAL')
    diff_col = diff_color_map.get(difficulty, (255, 255, 255))
    
    diff_title = small_font.render("DIFFICULTY", True, (150, 150, 160))
    diff_val = font.render(diff_str, True, diff_col)
    screen.blit(diff_title, (220, SCREEN_HEIGHT + 8))
    screen.blit(diff_val, (220, SCREEN_HEIGHT + 25))

    # 3. 점수 (SCORE) 및 적 수
    score_title = small_font.render("SCORE", True, (150, 150, 160))
    score_val = font.render(f"{score:05d} PTS", True, COLOR_AMMO)
    screen.blit(score_title, (360, SCREEN_HEIGHT + 8))
    screen.blit(score_val, (360, SCREEN_HEIGHT + 25))

    # 4. 생존한 적 표시
    enemy_title = small_font.render("ENEMIES", True, (150, 150, 160))
    enemy_val = font.render(f"{active_enemies:02d} ALIVE", True, (240, 240, 240))
    screen.blit(enemy_title, (500, SCREEN_HEIGHT + 8))
    screen.blit(enemy_val, (500, SCREEN_HEIGHT + 25))


def draw_weapon(screen, shoot_frame, dt):
    """화면 하단 중앙에 레트로풍 3D 총기를 드로잉합니다."""
    center_x = SCREEN_WIDTH // 2
    bottom_y = SCREEN_HEIGHT

    # 기본 파라미터
    weapon_w = 80
    weapon_h = 130
    
    # 사격 반동에 따른 위치 오프셋 및 발사 플래시
    offset_y = 0
    if shoot_frame > 0:
        # 격발 반동 프레임에 따라 총이 아래로 움직임
        if shoot_frame == 1:
            offset_y = 15
            # 격발 화염 그리기 (노란색/빨간색 플래시)
            pygame.draw.polygon(screen, (255, 255, 100), [
                (center_x - 30, bottom_y - weapon_h - 10),
                (center_x + 30, bottom_y - weapon_h - 10),
                (center_x + 10, bottom_y - weapon_h - 50),
                (center_x - 10, bottom_y - weapon_h - 50)
            ])
            pygame.draw.polygon(screen, (255, 120, 0), [
                (center_x - 15, bottom_y - weapon_h - 10),
                (center_x + 15, bottom_y - weapon_h - 10),
                (center_x, bottom_y - weapon_h - 35)
            ])
        elif shoot_frame == 2:
            offset_y = 8
        elif shoot_frame == 3:
            offset_y = 3

    # 총 몸체 (그라데이션 회색 다각형 조립)
    # 총열 (Barrel)
    pygame.draw.rect(screen, (40, 40, 45), (center_x - 10, bottom_y - weapon_h + offset_y, 20, weapon_h - 20))
    pygame.draw.rect(screen, (60, 60, 65), (center_x - 7, bottom_y - weapon_h + offset_y, 14, weapon_h - 20))
    pygame.draw.circle(screen, (20, 20, 20), (center_x, bottom_y - weapon_h + offset_y), 7) # 총구 입구
    
    # 개당판/총 본체 수직 다각형
    pygame.draw.polygon(screen, (80, 80, 85), [
        (center_x - 25, bottom_y + offset_y),
        (center_x + 25, bottom_y + offset_y),
        (center_x + 15, bottom_y - 45 + offset_y),
        (center_x - 15, bottom_y - 45 + offset_y)
    ])
    pygame.draw.polygon(screen, (100, 100, 105), [
        (center_x - 15, bottom_y + offset_y),
        (center_x + 15, bottom_y + offset_y),
        (center_x + 8, bottom_y - 45 + offset_y),
        (center_x - 8, bottom_y - 45 + offset_y)
    ])


def draw_minimap(screen, player, map_obj, enemies):
    """화면 우상단에 실시간 인공지능 검증용 2D 그리드 미니맵을 조그맣게 렌더링합니다."""
    cell_size = 5
    map_w = map_obj.get_width() * cell_size
    map_h = map_obj.get_height() * cell_size
    
    start_x = SCREEN_WIDTH - map_w - 15
    start_y = 15

    # 미니맵 배경
    pygame.draw.rect(screen, (10, 10, 15), (start_x - 4, start_y - 4, map_w + 8, map_h + 8))
    pygame.draw.rect(screen, (50, 50, 60), (start_x - 4, start_y - 4, map_w + 8, map_h + 8), 1)

    # 맵 그리기
    for r in range(map_obj.get_height()):
        for c in range(map_obj.get_width()):
            if map_obj.grid[r][c] > 0:
                pygame.draw.rect(screen, (70, 75, 90), (start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size))
            else:
                pygame.draw.rect(screen, (20, 20, 25), (start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size))

    # 적 위치 드로잉 (빨간 점)
    for enemy in enemies:
        if enemy.state != EnemyState.DEAD:
            ex = int(start_x + enemy.x * cell_size)
            ey = int(start_y + enemy.y * cell_size)
            pygame.draw.circle(screen, (255, 0, 0), (ex, ey), 2)

    # 플레이어 위치 드로잉 (노란 점 및 방향 지시선)
    px = int(start_x + player.x * cell_size)
    py = int(start_y + player.y * cell_size)
    pygame.draw.circle(screen, (240, 200, 0), (px, py), 2)
    
    line_len = 5
    lx = px + int(math.cos(player.angle) * line_len)
    ly = py + int(math.sin(player.angle) * line_len)
    pygame.draw.line(screen, (255, 255, 0), (px, py), (lx, ly), 1)


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Python Doom 3D (A* AI & Raycasting)")
    clock = pygame.time.Clock()
    
    # 마우스 포인터 캡처 및 화면 밖 탈출 방지
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    mouse_captured = True

    # 1. 인스턴스 초기화
    game_map = Map()
    px, py = game_map.player_spawn
    player = Player(px, py)
    
    enemy_manager = EnemyManager(difficulty='medium')
    enemy_manager.spawn_enemies(game_map)

    # 무기 격발 메커니즘 변수
    shoot_timer = 0.0
    shoot_frame = 0  # 0: 대기, 1: 격발, 2: 반동 하강, 3: 원위치
    
    player_hp = 100
    player_score = 0
    game_over = False
    game_clear = False
    
    font_large = pygame.font.SysFont("malgungothic", 30, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 16)

    # 메인 루프
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # 최대 60FPS 및 델타 타임 변환
        
        # --- 1. 이벤트 처리 ---
        mouse_rel_x = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # 마우스 해제 / 재캡처 토글
                    mouse_captured = not mouse_captured
                    pygame.mouse.set_visible(not mouse_captured)
                    pygame.event.set_grab(mouse_captured)
                    
                elif event.key == pygame.K_r:
                    # 게임 리셋
                    player.x, player.y = game_map.player_spawn
                    player.angle = 0.0
                    player_hp = 100
                    player_score = 0
                    enemy_manager.spawn_enemies(game_map)
                    shoot_frame = 0
                    game_over = False
                    game_clear = False
                    
                # 난이도 키보드 즉시 조절 (1, 2, 3)
                if not game_over and not game_clear:
                    if event.key == pygame.K_1:
                        enemy_manager.set_difficulty('easy')
                    elif event.key == pygame.K_2:
                        enemy_manager.set_difficulty('medium')
                    elif event.key == pygame.K_3:
                        enemy_manager.set_difficulty('hard')
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 총기 사격 격발 처리 (마우스가 잡혀 있고 활성 게임 상태일 때)
                if mouse_captured and not game_over and not game_clear and event.button == 1:
                    if shoot_frame == 0:  # 사격 준비 상태일 때만
                        shoot_frame = 1
                        shoot_timer = 0.0
                        
                        # --- 3D 사격 피격 판정 (Center-pixel Hitscan) ---
                        # 플레이어가 바라보는 방향(정면)에 가장 가까이 있는 적 검사
                        hit_enemy = None
                        min_dist_to_enemy = float('inf')
                        
                        fov = player.fov
                        active_enemies = enemy_manager.get_active_enemies()
                        
                        for enemy in active_enemies:
                            dx = enemy.x - player.x
                            dy = enemy.y - player.y
                            
                            # 적과 플레이어 사이의 실제 월드 각도
                            target_angle = math.atan2(dy, dx)
                            # 플레이어 시선과의 델타 각도 정규화
                            angle_diff = target_angle - player.angle
                            angle_diff = (angle_diff + math.pi) % math.tau - math.pi
                            
                            # 델타 각도가 시야각 범위 내에 있고, 플레이어 전방에 위치하는지 검사
                            if abs(angle_diff) < fov / 2.0:
                                # 카메라 좌표계의 깊이(거리) 계산
                                dist = dx * math.cos(player.angle) + dy * math.sin(player.angle)
                                if dist > 0.3: # 지나치게 가까운 픽셀 판정 제외
                                    # 화면 중앙 대비 오프셋
                                    sprite_x = dx * math.sin(player.angle) - dy * math.cos(player.angle)
                                    # 화면 가로 기준 투영 X 오프셋 비율
                                    proj_ratio = sprite_x / (dist * math.tan(fov / 2.0))
                                    
                                    # 몬스터의 3D 너비 범위 내(조준선인 중앙에서 피격 허용 오프셋 이내)인지 판정
                                    # 거리가 멀어질수록 탄착군 허용 편차가 엄격해집니다.
                                    hit_limit = 0.3 / dist # 적의 가로 3D 시각 크기 폭
                                    hit_limit = max(0.04, min(0.35, hit_limit)) # 피격 반경 보정 범위 제한
                                    
                                    if abs(proj_ratio) < hit_limit:
                                        if dist < min_dist_to_enemy:
                                            # 벽보다 가까이 있는 적인지 레이캐스터와 비교
                                            # 화면 정중앙 픽셀(NUM_RAYS // 2)의 벽 거리 데이터 조회
                                            # (main_3d 루프에 들어가므로 임시 체크나 이후 raycast 갱신 데이터 사용)
                                            # 여기서는 단순 가시 거리로 먼저 1차 필터링
                                            min_dist_to_enemy = dist
                                            hit_enemy = enemy

                        if hit_enemy:
                            # 3D 피격 타격 발생!
                            damage = 35
                            score_gain = hit_enemy.take_damage(damage)
                            player_score += score_gain

            elif event.type == pygame.MOUSEMOTION:
                # 마우스가 캡처된 상태일 때 시선 회전량 누적
                if mouse_captured:
                    mouse_rel_x, _ = pygame.mouse.get_rel()

        # 마우스 캡처 모드가 풀렸을 때 강제 복귀 지원
        if pygame.mouse.get_pressed()[0] and not mouse_captured:
            mouse_captured = True
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

        # --- 2. 물리 및 AI 상태 업데이트 ---
        if not game_over and not game_clear:
            keys = pygame.key.get_pressed()
            # 플레이어 이동/시선 갱신 (A팀 player.py)
            player.update(keys, mouse_rel_x, game_map, dt)
            
            # 적 캐릭터들 A* AI 업데이트 (B팀 enemy.py & pathfinding.py)
            enemy_manager.update_all((player.x, player.y), game_map, dt)
            
            # 플레이어 피격 처리 (적이 근접 공격 영역 내에서 공격 중일 때 데미지 누적)
            for enemy in enemy_manager.get_active_enemies():
                if enemy.state == EnemyState.ATTACK and enemy.attack_cooldown >= enemy.attack_rate - 0.02:
                    player_hp -= enemy.damage
                    if player_hp <= 0:
                        player_hp = 0
                        game_over = True
                        
            # 승리 조건: 모든 적 처치 완료
            if len(enemy_manager.get_active_enemies()) == 0:
                game_clear = True

        # 무기 사격 애니메이션 타이머 갱신
        if shoot_frame > 0:
            shoot_timer += dt
            if shoot_timer >= 0.08: # 0.08초마다 애니메이션 다음 프레임 전진
                shoot_timer = 0.0
                shoot_frame += 1
                if shoot_frame > 3:
                    shoot_frame = 0 # 격발 애니메이션 리셋

        # --- 3. 3D 그래픽스 렌더링 파이프라인 ---
        screen.fill((15, 15, 20))
        
        # 3.1. 3D 벽면 레이캐스팅 렌더링 (depth_buffer 및 Z-Buffer 획득)
        depth_buffer = raycast(screen, player, game_map)
        
        # 3.2. 3D 적 스프라이트 투영 렌더링 (Z-Buffer를 고려한 벽 가림 연산 포함)
        render_enemies(screen, player, enemy_manager.enemies, depth_buffer)
        
        # 3.3. 3D 십자 조준선(Crosshair) 그리기 (레트로 FPS 필수)
        pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 8, HALF_HEIGHT), (SCREEN_WIDTH // 2 + 8, HALF_HEIGHT), 2)
        pygame.draw.line(screen, (0, 255, 0), (SCREEN_WIDTH // 2, HALF_HEIGHT - 8), (SCREEN_WIDTH // 2, HALF_HEIGHT + 8), 2)
        
        # 3.4. 총기 및 격발 애니메이션 오버레이 렌더링
        draw_weapon(screen, shoot_frame, dt)
        
        # 3.5. 우상단 실시간 전술 미니맵 오버레이 렌더링
        draw_minimap(screen, player, game_map, enemy_manager.enemies)
        
        # 3.6. 하단 레트로 HUD 렌더링 (체력, 점수, 생존 상황)
        draw_hud(screen, player_hp, player_score, enemy_manager.difficulty, len(enemy_manager.get_active_enemies()))

        # --- 4. 게임 오버 / 클리어 연출 및 도움말 화면 ---
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))
            
            text_title = font_large.render("YOU DIED", True, (255, 50, 50))
            text_sub1 = font_small.render("적이 플레이어를 파괴했습니다.", True, (230, 230, 230))
            text_sub2 = font_small.render("[R] 키를 눌러 다시 도전하세요.", True, (150, 150, 160))
            
            screen.blit(text_title, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 50))
            screen.blit(text_sub1, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2))
            screen.blit(text_sub2, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 30))
            
        elif game_clear:
            overlay = pygame.Surface((SCREEN_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 50, 0, 150))
            screen.blit(overlay, (0, 0))
            
            text_title = font_large.render("VICTORY!", True, (0, 255, 120))
            text_sub1 = font_small.render("맵 내의 모든 적을 섬멸했습니다.", True, (230, 230, 230))
            text_sub2 = font_small.render(f"최종 획득 점수: {player_score} PTS", True, COLOR_AMMO)
            text_sub3 = font_small.render("[R] 키를 눌러 새로운 게임을 시작하세요.", True, (170, 170, 170))
            
            screen.blit(text_title, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 60))
            screen.blit(text_sub1, (SCREEN_WIDTH // 2 - 115, SCREEN_HEIGHT // 2 - 10))
            screen.blit(text_sub2, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 15))
            screen.blit(text_sub3, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 45))

        # 마우스 커서 일시 해제 상태 안내 문구
        if not mouse_captured and not game_over and not game_clear:
            inf_text = font_small.render("[PAUSE] 마우스 조작이 정지되었습니다. 창을 클릭하면 다시 복귀합니다.", True, (255, 255, 100))
            screen.blit(inf_text, (20, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
