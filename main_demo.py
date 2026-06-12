# main_demo.py
"""
B팀 검증용: 2D 통합 비주얼 데모
이 파일은 B팀의 map.py, pathfinding.py, enemy.py가 잘 작동하는지 2D 시각화로 직접 확인하고
다른 팀원들(A팀: 엔진, C팀: UI/게임상태)에게 '이렇게 모듈을 연동하면 된다'는 예시를 보여주는 통합 데모 파일입니다.

조작 방법:
- [W, A, S, D] 또는 방향키: 플레이어 이동 (노란색 원)
- [마우스 움직임]: 플레이어 시선 방향 회전
- [마우스 좌클릭]: 총 발사 (C팀 무기 연동 예시, 클릭한 방향의 적에게 피해 제공)
- [키보드 1, 2, 3]: 실시간 난이도 변경 (1: 쉬움, 2: 보통, 3: 어려움)
- [R]: 게임 재시작 (플레이어 HP가 0이 되어 게임 오버 되었을 때)
"""

import sys
import math
import pygame
from map import Map
from enemy import EnemyManager, EnemyState

# 화면 설정
GRID_RENDER_SIZE = 32  # 맵 한 칸을 그릴 픽셀 크기
MAP_WIDTH_PX = 16 * GRID_RENDER_SIZE  # 16칸 * 32 = 512
SIDEBAR_WIDTH = 250
WINDOW_WIDTH = MAP_WIDTH_PX + SIDEBAR_WIDTH
WINDOW_HEIGHT = 16 * GRID_RENDER_SIZE  # 512
FPS = 60

# 색상 상수
COLOR_BG = (15, 15, 20)
COLOR_WALL = (60, 65, 80)
COLOR_FLOOR = (25, 25, 30)
COLOR_PLAYER = (240, 200, 0)
COLOR_ENEMY_PATROL = (200, 100, 0)
COLOR_ENEMY_CHASE = (220, 20, 20)
COLOR_ENEMY_ATTACK = (255, 100, 100)
COLOR_PATH = (0, 255, 120)
COLOR_SIDEBAR_BG = (28, 28, 38)
COLOR_TEXT_PRIMARY = (240, 240, 240)
COLOR_TEXT_MUTED = (150, 150, 160)
COLOR_HEALTH_BAR = (220, 40, 40)

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Doom-like Game B-Team (Map & Enemy AI) Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("malgungothic", 16) # 한글 지원 폰트
    title_font = pygame.font.SysFont("malgungothic", 20, bold=True)
    
    # 1. 맵 생성
    game_map = Map()
    
    # 2. 플레이어 상태 정의 (임시 - A팀 player.py 역할)
    px, py = game_map.player_spawn
    player_hp = 100
    player_max_hp = 100
    player_speed = 3.5  # 타일/초
    player_angle = 0.0  # 라디안 단위 방향
    player_score = 0     # C팀 점수 예시
    
    # 3. 적 매니저 생성 및 스폰 (B팀 enemy.py)
    enemy_manager = EnemyManager(difficulty='medium')
    enemy_manager.spawn_enemies(game_map)
    
    # 사격 피격선 시각화를 위한 궤적 저장용 리스트
    shot_tracers = [] # [(start_pos, end_pos, timer), ...]
    
    game_over = False
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # 델타 타임을 초 단위로 변환
        
        # --- 1. 이벤트 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # 게임 재시작
                        px, py = game_map.player_spawn
                        player_hp = 100
                        player_score = 0
                        enemy_manager.spawn_enemies(game_map)
                        shot_tracers.clear()
                        game_over = False
                else:
                    # 실시간 난이도 조절 테스트
                    if event.key == pygame.K_1:
                        enemy_manager.set_difficulty('easy')
                    elif event.key == pygame.K_2:
                        enemy_manager.set_difficulty('medium')
                    elif event.key == pygame.K_3:
                        enemy_manager.set_difficulty('hard')
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 총기 발사 테스트 (C팀 weapon.py 연동용 예시)
                if not game_over and event.button == 1: # 마우스 좌클릭
                    # 플레이어가 바라보는 방향으로 광선을 쏘아 가장 가까운 적을 맞춤 (히트스캔)
                    ray_angle = player_angle
                    # 광선 시작점
                    rx, ry = px, py
                    step_size = 0.05
                    max_distance = 15.0 # 최대 사거리
                    
                    hit_enemy = None
                    distance_traveled = 0.0
                    
                    # 광선 전진
                    while distance_traveled < max_distance:
                        rx += math.cos(ray_angle) * step_size
                        ry += math.sin(ray_angle) * step_size
                        distance_traveled += step_size
                        
                        # 벽 충돌 확인
                        if game_map.is_wall(rx, ry):
                            break
                            
                        # 적 충돌 확인 (적 캐릭터와 광선 끝점의 거리 체크)
                        for enemy in enemy_manager.get_active_enemies():
                            edist = math.sqrt((enemy.x - rx)**2 + (enemy.y - ry)**2)
                            if edist < 0.4:  # 적 피격 판정 반지름
                                hit_enemy = enemy
                                break
                        
                        if hit_enemy:
                            break
                    
                    # 피격선 시각화용 데이터 저장
                    end_x = rx * GRID_RENDER_SIZE
                    end_y = ry * GRID_RENDER_SIZE
                    start_x = px * GRID_RENDER_SIZE
                    start_y = py * GRID_RENDER_SIZE
                    shot_tracers.append(((start_x, start_y), (end_x, end_y), 0.15))
                    
                    if hit_enemy:
                        damage_amount = 34  # 발당 데미지
                        score_earned = hit_enemy.take_damage(damage_amount)
                        player_score += score_earned
        
        # --- 2. 플레이어 및 적 AI 업데이트 ---
        if not game_over:
            # 마우스 위치 기반 플레이어 방향 각도 계산
            mx, my = pygame.mouse.get_pos()
            px_screen = px * GRID_RENDER_SIZE
            py_screen = py * GRID_RENDER_SIZE
            player_angle = math.atan2(my - py_screen, mx - px_screen)

            # 플레이어 키보드 이동 입력 (임시 A팀 이동 로직)
            keys = pygame.key.get_pressed()
            move_x, move_y = 0.0, 0.0
            
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y -= 1.0
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1.0
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1.0
                
            # 대각선 이동 정규화
            move_dist = math.sqrt(move_x**2 + move_y**2)
            if move_dist > 0:
                dx = (move_x / move_dist) * player_speed * dt
                dy = (move_y / move_dist) * player_speed * dt
                
                # 충돌 판정을 통한 이동 제한 (B팀 map.py.is_wall 활용)
                new_x = px + dx
                new_y = py + dy
                
                # 플레이어 크기(반지름 0.2)를 고려한 미끄러짐 충돌 처리
                buffer = 0.2
                # X축 검사
                if not game_map.is_wall(new_x + (buffer if dx > 0 else -buffer), py):
                    px = new_x
                # Y축 검사
                if not game_map.is_wall(px, new_y + (buffer if dy > 0 else -buffer)):
                    py = new_y
            
            # 적들 AI 업데이트 (B팀 enemy.py)
            enemy_manager.update_all((px, py), game_map, dt)
            
            # 플레이어 피격 처리 (적이 공격 범위에 있어서 플레이어를 공격하는지 시뮬레이션)
            # enemy.py에서 ATTACK 상태인 적들이 플레이어 HP를 깎습니다.
            for enemy in enemy_manager.get_active_enemies():
                if enemy.state == EnemyState.ATTACK and enemy.attack_cooldown >= enemy.attack_rate - 0.02:
                    player_hp -= enemy.damage
                    if player_hp <= 0:
                        player_hp = 0
                        game_over = True
        
        # 피격선 수명 타이머 갱신
        for tracer in list(shot_tracers):
            start_pos, end_pos, time_left = tracer
            time_left -= dt
            shot_tracers.remove(tracer)
            if time_left > 0:
                shot_tracers.append((start_pos, end_pos, time_left))

        # --- 3. 2D 맵 및 오브젝트 렌더링 ---
        screen.fill(COLOR_BG)
        
        # 맵 타일 렌더링
        for r in range(game_map.get_height()):
            for c in range(game_map.get_width()):
                tile = game_map.get_wall_type(c, r)
                rect = pygame.Rect(c * GRID_RENDER_SIZE, r * GRID_RENDER_SIZE, GRID_RENDER_SIZE, GRID_RENDER_SIZE)
                if tile > 0:
                    # 벽 렌더링
                    pygame.draw.rect(screen, COLOR_WALL, rect)
                    pygame.draw.rect(screen, (40, 45, 55), rect, 1) # 테두리
                else:
                    # 바닥 렌더링
                    pygame.draw.rect(screen, COLOR_FLOOR, rect)
                    pygame.draw.rect(screen, (20, 20, 22), rect, 1) # 미세한 바닥 격자선
        
        # 적의 A* 추적 경로 시각화 (B팀의 핵심 인공지능 검증)
        for enemy in enemy_manager.get_active_enemies():
            if enemy.path and len(enemy.path) > 1:
                # 경로에 있는 타일들의 중심점을 선으로 연결하여 표시
                pts = [(col * GRID_RENDER_SIZE + GRID_RENDER_SIZE // 2, row * GRID_RENDER_SIZE + GRID_RENDER_SIZE // 2) for col, row in enemy.path]
                if len(pts) >= 2:
                    pygame.draw.lines(screen, COLOR_PATH, False, pts, 2)
        
        # 총 발사 흔적선(Tracer) 그리기
        for start_pos, end_pos, _ in shot_tracers:
            pygame.draw.line(screen, (255, 255, 100), start_pos, end_pos, 3)
            pygame.draw.circle(screen, (255, 100, 0), (int(end_pos[0]), int(end_pos[1])), 4)
            
        # 적 캐릭터 렌더링 (B팀 enemy.py)
        for enemy in enemy_manager.enemies:
            ex_scr = int(enemy.x * GRID_RENDER_SIZE)
            ey_scr = int(enemy.y * GRID_RENDER_SIZE)
            
            if enemy.state == EnemyState.DEAD:
                # 사망한 적은 회색 X로 표시
                pygame.draw.line(screen, (80, 80, 80), (ex_scr - 8, ey_scr - 8), (ex_scr + 8, ey_scr + 8), 3)
                pygame.draw.line(screen, (80, 80, 80), (ex_scr + 8, ey_scr - 8), (ex_scr - 8, ey_scr + 8), 3)
                continue
                
            # 상태에 따라 색상 다르게 표시
            if enemy.state == EnemyState.ATTACK:
                color = COLOR_ENEMY_ATTACK
            elif enemy.state == EnemyState.CHASE:
                color = COLOR_ENEMY_CHASE
            else:
                color = COLOR_ENEMY_PATROL
                
            # 적의 몸체 그리기
            pygame.draw.circle(screen, color, (ex_scr, ey_scr), 10)
            
            # 적 머리 방향 (플레이어를 향해 조준하는 것을 보여주기용)
            angle_to_player = math.atan2(py - enemy.y, px - enemy.x)
            hx = ex_scr + int(math.cos(angle_to_player) * 12)
            hy = ey_scr + int(math.sin(angle_to_player) * 12)
            pygame.draw.line(screen, (255, 255, 255), (ex_scr, ey_scr), (hx, hy), 2)
            
            # 적 HP 바 표시
            hp_ratio = enemy.hp / enemy.max_hp
            pygame.draw.rect(screen, (50, 0, 0), (ex_scr - 12, ey_scr - 16, 24, 4))
            pygame.draw.rect(screen, (255, 0, 0), (ex_scr - 12, ey_scr - 16, int(24 * hp_ratio), 4))
            
            # 적 위에 상태 텍스트 작게 띄우기
            state_map = {EnemyState.PATROL: "순찰", EnemyState.CHASE: "추적", EnemyState.ATTACK: "공격"}
            st_text = font.render(state_map[enemy.state], True, COLOR_TEXT_PRIMARY)
            screen.blit(st_text, (ex_scr - 10, ey_scr - 30))

        # 플레이어 캐릭터 렌더링 (임시)
        px_scr = int(px * GRID_RENDER_SIZE)
        py_scr = int(py * GRID_RENDER_SIZE)
        # 플레이어 본체
        pygame.draw.circle(screen, COLOR_PLAYER, (px_scr, py_scr), 8)
        # 플레이어 시선 방향 레이(짧게)
        lx = px_scr + int(math.cos(player_angle) * 15)
        ly = py_scr + int(math.sin(player_angle) * 15)
        pygame.draw.line(screen, (255, 255, 0), (px_scr, py_scr), (lx, ly), 3)

        # --- 4. 사이드바 정보 패널 렌더링 ---
        sidebar_rect = pygame.Rect(MAP_WIDTH_PX, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, sidebar_rect)
        pygame.draw.line(screen, (50, 50, 60), (MAP_WIDTH_PX, 0), (MAP_WIDTH_PX, WINDOW_HEIGHT), 2)
        
        # 텍스트 출력 유틸리티
        y_offset = 20
        def draw_text(text, is_title=False, color=COLOR_TEXT_PRIMARY):
            nonlocal y_offset
            renderer = title_font if is_title else font
            surf = renderer.render(text, True, color)
            screen.blit(surf, (MAP_WIDTH_PX + 20, y_offset))
            y_offset += 30 if is_title else 22

        draw_text("Doom 2D AI 데모", is_title=True, color=(0, 255, 200))
        draw_text("B팀 개발 결과 검증")
        draw_text("-" * 25, color=COLOR_TEXT_MUTED)
        
        # 플레이어 스태츠
        draw_text("플레이어 정보", is_title=True)
        draw_text(f"위치: ({px:.1f}, {py:.1f})")
        draw_text(f"점수: {player_score} pts", color=(255, 215, 0))
        
        # 체력바
        draw_text(f"체력 (HP): {player_hp} / {player_max_hp}")
        pygame.draw.rect(screen, (50, 10, 10), (MAP_WIDTH_PX + 20, y_offset, 200, 15))
        hp_w = int(200 * (player_hp / player_max_hp))
        if hp_w > 0:
            pygame.draw.rect(screen, COLOR_HEALTH_BAR, (MAP_WIDTH_PX + 20, y_offset, hp_w, 15))
        y_offset += 25
        
        draw_text("-" * 25, color=COLOR_TEXT_MUTED)
        
        # AI 정보 & 난이도 조절
        draw_text("AI & 난이도 설정", is_title=True)
        diff_str = "보통 (Medium)"
        diff_color = (0, 255, 120)
        if enemy_manager.difficulty == 'easy':
            diff_str = "쉬움 (Easy)"
            diff_color = (0, 180, 255)
        elif enemy_manager.difficulty == 'hard':
            diff_str = "어려움 (Hard)"
            diff_color = (255, 50, 50)
            
        draw_text(f"현재 난이도: {diff_str}", color=diff_color)
        draw_text("난이도 변경 단축키:")
        draw_text("  [1] 쉬움  [2] 보통  [3] 어려움", color=COLOR_TEXT_MUTED)
        
        # 생존 상태
        active_count = len(enemy_manager.get_active_enemies())
        total_count = len(enemy_manager.enemies)
        draw_text(f"생존한 적: {active_count} / {total_count} 마리")
        
        draw_text("-" * 25, color=COLOR_TEXT_MUTED)
        
        # 도움말
        draw_text("조작법 도움말", is_title=True)
        draw_text("이동: W, A, S, D", color=COLOR_TEXT_MUTED)
        draw_text("조준: 마우스 회전", color=COLOR_TEXT_MUTED)
        draw_text("발사: 마우스 좌클릭", color=COLOR_TEXT_MUTED)
        
        # 게임 오버 오버레이
        if game_over:
            # 반투명 어두운 화면 씌우기
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            go_text1 = title_font.render("GAME OVER", True, (255, 50, 50))
            go_text2 = font.render("적이 플레이어를 쓰러뜨렸습니다.", True, COLOR_TEXT_PRIMARY)
            go_text3 = font.render("[R] 키를 눌러 다시 도전하세요.", True, COLOR_TEXT_MUTED)
            
            screen.blit(go_text1, (MAP_WIDTH_PX // 2 - 60, WINDOW_HEIGHT // 2 - 40))
            screen.blit(go_text2, (MAP_WIDTH_PX // 2 - 110, WINDOW_HEIGHT // 2))
            screen.blit(go_text3, (MAP_WIDTH_PX // 2 - 110, WINDOW_HEIGHT // 2 + 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
