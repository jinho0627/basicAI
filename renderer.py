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
        
        # 벽 및 문 색상 (더 선명)
        self.wall_colors = {
            1: (180, 140, 120),  # 따뜻한 돌벽
            2: (120, 120, 160),  # 푸른 벽
            3: (160, 100, 100),  # 붉은 벽
            4: (80, 90, 100),    # 철제 자동문
            5: (180, 140, 120),  # 비밀문 (돌벽 1번과 동일 색상으로 위장)
        }
        
        # ━━━ 부드러운 렌더링 ━━━
        self.fog_distance = 20.0      # 안개 거리
        self.min_brightness = 0.15    # 최소 밝기

        # ━━━ 스프라이트 텍스처 생성 ━━━
        self._create_sprite_textures()
    
    def _create_sprite_textures(self):
        """적 및 투사체의 2D 스프라이트 텍스처를 미리 생성하여 캐싱합니다."""
        self.sprite_textures = {}
        font = pygame.font.SysFont("Courier New", 64, bold=True)

        # 1. C학점 적 (노랑-초록 슬라임 몬스터)
        surf_c = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_c, (0, 0, 0, 80), (14, 100, 100, 20))
        for r in range(50, 0, -4):
            color = (200 + r, 230 - r, 30)
            pygame.draw.circle(surf_c, color, (64, 64), r)
        pygame.draw.circle(surf_c, (255, 255, 255), (44, 50), 10)
        pygame.draw.circle(surf_c, (255, 255, 255), (84, 50), 10)
        pygame.draw.circle(surf_c, (0, 0, 0), (44, 50), 4)
        pygame.draw.circle(surf_c, (0, 0, 0), (84, 50), 4)
        pygame.draw.arc(surf_c, (0, 0, 0), (49, 70, 30, 20), 0, math.pi, 3)
        text_c = font.render("C", True, (0, 0, 0))
        surf_c.blit(text_c, (64 - text_c.get_width() // 2, 64 - text_c.get_height() // 2 + 12))
        self.sprite_textures['C'] = surf_c

        # 2. D학점 적 (주황색 유령 몬스터)
        surf_d = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_d, (0, 0, 0, 80), (14, 105, 100, 18))
        for r in range(50, 0, -4):
            color = (240, 140 - r, 20)
            pygame.draw.circle(surf_d, color, (64, 55), r)
        pygame.draw.polygon(surf_d, (240, 100, 20), [
            (14, 55), (34, 100), (49, 85), (64, 100), (79, 85), (94, 100), (114, 55)
        ])
        pygame.draw.circle(surf_d, (255, 255, 255), (44, 45), 10)
        pygame.draw.circle(surf_d, (255, 255, 255), (84, 45), 10)
        pygame.draw.circle(surf_d, (0, 0, 0), (44, 47), 4)
        pygame.draw.circle(surf_d, (0, 0, 0), (84, 47), 4)
        pygame.draw.rect(surf_d, (240, 100, 20), (34, 33, 20, 7))
        pygame.draw.rect(surf_d, (240, 100, 20), (74, 33, 20, 7))
        pygame.draw.ellipse(surf_d, (0, 0, 0), (54, 68, 16, 22))
        text_d = font.render("D", True, (255, 255, 255))
        surf_d.blit(text_d, (64 - text_d.get_width() // 2, 55 - text_d.get_height() // 2 + 10))
        self.sprite_textures['D'] = surf_d

        # 3. F학점 적 (거대한 붉은 악마 몬스터)
        surf_f = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_f, (0, 0, 0, 100), (14, 110, 100, 16))
        pygame.draw.polygon(surf_f, (120, 0, 0), [(30, 30), (10, 5), (45, 22)])
        pygame.draw.polygon(surf_f, (120, 0, 0), [(98, 30), (118, 5), (83, 22)])
        for r in range(50, 0, -4):
            color = (255 - r * 2, 10, 10)
            pygame.draw.circle(surf_f, color, (64, 64), r)
        pygame.draw.circle(surf_f, (255, 255, 0), (42, 52), 12)
        pygame.draw.circle(surf_f, (255, 255, 0), (86, 52), 12)
        pygame.draw.circle(surf_f, (255, 0, 0), (42, 52), 4)
        pygame.draw.circle(surf_f, (255, 0, 0), (86, 52), 4)
        pygame.draw.line(surf_f, (0, 0, 0), (28, 36), (54, 46), 4)
        pygame.draw.line(surf_f, (0, 0, 0), (100, 36), (74, 46), 4)
        pygame.draw.polygon(surf_f, (0, 0, 0), [(48, 80), (80, 80), (64, 98)])
        pygame.draw.polygon(surf_f, (255, 255, 255), [(52, 80), (58, 88), (64, 80)])
        pygame.draw.polygon(surf_f, (255, 255, 255), [(76, 80), (70, 88), (64, 80)])
        text_f = font.render("F", True, (255, 255, 255))
        surf_f.blit(text_f, (64 - text_f.get_width() // 2, 64 - text_f.get_height() // 2 + 10))
        self.sprite_textures['F'] = surf_f

        # 4. 투사체 (D학점의 학업 스트레스 폭발 파란 구체)
        surf_proj = pygame.Surface((32, 32), pygame.SRCALPHA)
        for r in range(14, 0, -2):
            color = (30 + r * 15, 120 + r * 8, 255, 255 - r * 5)
            pygame.draw.circle(surf_proj, color, (16, 16), r)
        pygame.draw.circle(surf_proj, (255, 255, 255), (16, 16), 4)
        self.sprite_textures['proj'] = surf_proj

        # 5. 교수님 적 (화난 교수님)
        surf_p = pygame.Surface((128, 128), pygame.SRCALPHA)
        # 그림자
        pygame.draw.ellipse(surf_p, (0, 0, 0, 120), (10, 112, 108, 16))
        
        # 1) 머리/몸통 (회색 정장 차림)
        # 정장 몸통
        pygame.draw.polygon(surf_p, (50, 50, 60), [(24, 115), (104, 115), (84, 75), (44, 75)])
        # 와이셔츠
        pygame.draw.polygon(surf_p, (240, 240, 240), [(48, 75), (80, 75), (64, 95)])
        # 빨간 넥타이
        pygame.draw.polygon(surf_p, (200, 20, 20), [(61, 90), (67, 90), (69, 112), (64, 115), (59, 112)])
        
        # 2) 화가 나 얼굴 (빨개진 얼굴 - 그라데이션)
        for r in range(45, 0, -4):
            color = (255, max(0, 180 - r * 3), max(0, 160 - r * 3))
            pygame.draw.circle(surf_p, color, (64, 50), r)
            
        # 3) 머리카락 (대머리 스타일 - 옆머리만 회색으로 풍성)
        # 왼편 옆머리
        pygame.draw.ellipse(surf_p, (100, 100, 100), (12, 40, 24, 35))
        pygame.draw.ellipse(surf_p, (180, 180, 180), (14, 45, 18, 25))
        # 오른편 옆머리
        pygame.draw.ellipse(surf_p, (100, 100, 100), (92, 40, 24, 35))
        pygame.draw.ellipse(surf_p, (180, 180, 180), (96, 45, 18, 25))
        
        # 4) 성난 눈썹과 안경, 불타는 눈
        # 안경테 (검정)
        pygame.draw.rect(surf_p, (30, 30, 30), (32, 40, 26, 18), 3) # 왼쪽 안경알
        pygame.draw.rect(surf_p, (30, 30, 30), (70, 40, 26, 18), 3) # 오른쪽 안경알
        pygame.draw.line(surf_p, (30, 30, 30), (58, 48), (70, 48), 3) # 안경 브릿지
        
        # 화난 눈 (안경알 안쪽에 불타는 노란색/빨간색 눈동자)
        pygame.draw.circle(surf_p, (255, 255, 0), (45, 49), 6)
        pygame.draw.circle(surf_p, (255, 0, 0), (45, 49), 2)
        pygame.draw.circle(surf_p, (255, 255, 0), (83, 49), 6)
        pygame.draw.circle(surf_p, (255, 0, 0), (83, 49), 2)
        
        # 성난 눈썹 (V자 모양으로 매우 화남)
        pygame.draw.line(surf_p, (0, 0, 0), (28, 32), (54, 42), 5)
        pygame.draw.line(surf_p, (0, 0, 0), (100, 32), (74, 42), 5)
        
        # 5) 크게 벌리고 소리치는 입
        pygame.draw.ellipse(surf_p, (20, 20, 20), (50, 68, 28, 20))
        # 뾰족한 이빨 (위에 두 개, 아래 두 개)
        pygame.draw.polygon(surf_p, (255, 255, 255), [(54, 68), (58, 74), (62, 68)])
        pygame.draw.polygon(surf_p, (255, 255, 255), [(74, 68), (70, 74), (66, 68)])
        
        # 6) 이마에 힘줄 (화난 혈관 마크)
        pygame.draw.line(surf_p, (180, 0, 0), (58, 22), (64, 26), 2)
        pygame.draw.line(surf_p, (180, 0, 0), (64, 26), (62, 32), 2)
        pygame.draw.line(surf_p, (180, 0, 0), (64, 26), (70, 24), 2)
        
        # P 텍스트 블릿
        text_p = font.render("P", True, (255, 0, 0))
        surf_p.blit(text_p, (64 - text_p.get_width() // 2, 50 - text_p.get_height() // 2))
        self.sprite_textures['P'] = surf_p

        # 6. 교수님의 F학점 투사체 (빨간색 F가 적힌 시험지)
        surf_proj_p = pygame.Surface((48, 48), pygame.SRCALPHA)
        # 흰색 종이 그리기
        pygame.draw.rect(surf_proj_p, (255, 255, 255), (6, 6, 36, 36))
        # 빨간색 테두리
        pygame.draw.rect(surf_proj_p, (200, 20, 20), (6, 6, 36, 36), 2)
        # 종이 안의 글씨 줄들 (회색 선들)
        pygame.draw.line(surf_proj_p, (150, 150, 150), (12, 14), (36, 14), 2)
        pygame.draw.line(surf_proj_p, (150, 150, 150), (12, 22), (28, 22), 2)
        pygame.draw.line(surf_proj_p, (150, 150, 150), (12, 30), (32, 30), 2)
        # 오른쪽 위에 커다란 F 학점 도장
        font_proj = pygame.font.SysFont("Courier New", 20, bold=True)
        text_f = font_proj.render("F", True, (255, 0, 0))
        surf_proj_p.blit(text_f, (28, 12))
        self.sprite_textures['proj_p'] = surf_proj_p

        # 7. 독 함정 (바닥의 초록색 독성 물질 웅덩이)
        surf_trap = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_trap, (0, 180, 0, 150), (14, 80, 100, 40))
        pygame.draw.ellipse(surf_trap, (0, 230, 0, 200), (24, 90, 80, 25))
        pygame.draw.ellipse(surf_trap, (150, 255, 150, 220), (39, 95, 50, 12))
        self.sprite_textures['trap'] = surf_trap

        # 8. A+ 학점 아이템 (금빛으로 빛나는 A+ 마크)
        surf_item_a = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_item_a, (255, 215, 0, 80), (14, 100, 100, 20))
        for r in range(40, 0, -4):
            color = (255, 200 + r, 50 - r)
            pygame.draw.circle(surf_item_a, color, (64, 64), r)
        pygame.draw.circle(surf_item_a, (255, 255, 255), (64, 64), 32, 2)
        font_item = pygame.font.SysFont("Courier New", 32, bold=True)
        text_ap = font_item.render("A+", True, (255, 0, 0))
        surf_item_a.blit(text_ap, (64 - text_ap.get_width() // 2, 64 - text_ap.get_height() // 2))
        self.sprite_textures['item_a'] = surf_item_a

        # 9. 학식 아이템 (식기 트레이 위에 밥, 국, 반찬)
        surf_item_h = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.ellipse(surf_item_h, (0, 0, 0, 60), (14, 100, 100, 20))
        pygame.draw.rect(surf_item_h, (170, 170, 180), (24, 60, 80, 50), border_radius=5)
        pygame.draw.rect(surf_item_h, (120, 120, 130), (24, 60, 80, 50), 3, border_radius=5)
        pygame.draw.circle(surf_item_h, (240, 240, 240), (44, 75), 14)
        pygame.draw.circle(surf_item_h, (139, 69, 19), (84, 75), 14)
        pygame.draw.ellipse(surf_item_h, (40, 180, 40), (38, 92, 16, 10))
        pygame.draw.ellipse(surf_item_h, (220, 40, 40), (74, 92, 16, 10))
        pygame.draw.arc(surf_item_h, (200, 200, 200), (38, 42, 12, 18), 0, math.pi, 2)
        pygame.draw.arc(surf_item_h, (200, 200, 200), (78, 42, 12, 18), 0, math.pi, 2)
        self.sprite_textures['item_h'] = surf_item_h
    
    def render_frame(self, screen, rays, player_x, player_y, player_angle, enemies=None, projectiles=None, game_map=None):
        """3D 화면 및 스프라이트(적, 투사체) 렌더링"""
        # 천장과 바닥 (그라디언트 효과)
        self._render_floor_ceiling(screen)
        
        # 벽 렌더링
        num_rays = len(rays)
        column_width = self.width / num_rays
        
        for i, ray in enumerate(rays):
            self._render_wall_slice(screen, i, column_width, ray, game_map)

        # 스프라이트(적, 투사체) 렌더링
        self._render_sprites(screen, rays, player_x, player_y, player_angle, enemies, projectiles, game_map)

    def _render_sprites(self, screen, rays, player_x, player_y, player_angle, enemies, projectiles, game_map=None):
        """적 및 투사체 스프라이트를 원근 정렬하여 렌더링"""
        sprites_to_render = []
        
        # 1. 활성화된 적 수집
        if enemies:
            for enemy in enemies:
                dx = enemy.x - player_x
                dy = enemy.y - player_y
                dist = math.sqrt(dx**2 + dy**2)
                sprites_to_render.append({
                    'x': enemy.x,
                    'y': enemy.y,
                    'dist': dist,
                    'type': enemy.grade,
                })
                
        # 2. 투사체 수집
        if projectiles:
            for proj in projectiles:
                dx = proj.x - player_x
                dy = proj.y - player_y
                dist = math.sqrt(dx**2 + dy**2)
                sprites_to_render.append({
                    'x': proj.x,
                    'y': proj.y,
                    'dist': dist,
                    'type': getattr(proj, 'type', 'proj'),
                })

        # 3. 독 함정 수집
        if game_map and hasattr(game_map, 'traps'):
            for trap in game_map.traps:
                dx = trap['x'] - player_x
                dy = trap['y'] - player_y
                dist = math.sqrt(dx**2 + dy**2)
                sprites_to_render.append({
                    'x': trap['x'],
                    'y': trap['y'],
                    'dist': dist,
                    'type': 'trap',
                })

        # 4. 아이템 수집
        if game_map and hasattr(game_map, 'items'):
            for item in game_map.items:
                dx = item['x'] - player_x
                dy = item['y'] - player_y
                dist = math.sqrt(dx**2 + dy**2)
                sprites_to_render.append({
                    'x': item['x'],
                    'y': item['y'],
                    'dist': dist,
                    'type': 'item_a' if item['type'] == 'A+' else 'item_h',
                })
                
        # 3. 원근 정렬 (거리가 먼 순으로 정렬 - Painter's Algorithm)
        sprites_to_render.sort(key=lambda s: s['dist'], reverse=True)
        
        # 4. 시야각(FOV) 설정
        fov = math.pi / 2.5  # 72도 FOV
        
        # 5. 각 스프라이트 투영 및 렌더링
        for sprite in sprites_to_render:
            dist = sprite['dist']
            if dist < 0.2:  # 너무 가까우면 제외
                continue
                
            dx = sprite['x'] - player_x
            dy = sprite['y'] - player_y
            
            # 플레이어 시선 벡터 기준 전방 거리 계산 (Fisheye 현상 방지)
            dist_x = dx * math.cos(player_angle) + dy * math.sin(player_angle)
            if dist_x <= 0.1:  # 플레이어 뒤에 있음
                continue
                
            # 상대 각도 구하기 및 정규화 [-pi, pi]
            sprite_angle = math.atan2(dy, dx)
            diff_angle = sprite_angle - player_angle
            diff_angle = (diff_angle + math.pi) % (2 * math.pi) - math.pi
            
            # 시야각(FOV)을 벗어나는 스프라이트는 조기 제외 (마진 0.5 라디안 적용)
            if abs(diff_angle) > fov / 2 + 0.5:
                continue
            
            # 화면의 가로 중앙 컬럼 계산
            screen_x = int((self.width / 2) + (diff_angle / fov) * self.width)
            
            # 스프라이트 크기 계산 (원근 스케일링 - 화면 가장자리 왜곡 방지를 위해 유클리드 거리 사용)
            sprite_height = int(self.game_height / dist)
            sprite_width = sprite_height

            # 원본 높이 기억 (바닥 정렬용)
            unscaled_height = sprite_height

            # 투사체, 독함정, 아이템 축소 및 납작화
            if sprite['type'] in ('proj', 'proj_p', 'trap', 'item_a', 'item_h'):
                if sprite['type'] == 'proj':
                    sf_w, sf_h = 0.25, 0.25
                elif sprite['type'] == 'proj_p':
                    sf_w, sf_h = 0.38, 0.38
                elif sprite['type'] == 'trap':
                    sf_w, sf_h = 1.1, 0.4  # 넓고 납작하게 (크기 확대)
                else:  # item_a, item_h
                    sf_w, sf_h = 0.4, 0.4
                sprite_width = int(sprite_width * sf_w)
                sprite_height = int(sprite_height * sf_h)
                
            if sprite_height <= 0 or sprite_width <= 0:
                continue
                
            # 화면 그리기 좌표 범위 설정
            if sprite['type'] in ('trap', 'item_a', 'item_h'):
                # 바닥에 정렬 (벽 아래 끝부분에 맞춤)
                bottom_y = self.half_height + unscaled_height // 2
                draw_start_y = bottom_y - sprite_height
                draw_end_y = bottom_y
            else:
                # 중앙에 정렬 (몬스터, 투사체 등)
                draw_start_y = self.half_height - sprite_height // 2
                draw_end_y = self.half_height + sprite_height // 2
            
            draw_start_x = screen_x - sprite_width // 2
            draw_end_x = screen_x + sprite_width // 2
            
            # 해당 타입 텍스처 불러오기
            tex = self.sprite_textures.get(sprite['type'])
            if not tex:
                continue
                
            # 크기에 맞게 텍스처 스케일링
            scaled_tex = pygame.transform.scale(tex, (sprite_width, sprite_height))
            
            # 컬럼별 가림 체크(1D Z-Buffer) 및 슬라이스 렌더링
            num_rays = len(rays)
            for col_x in range(draw_start_x, draw_end_x):
                if 0 <= col_x < self.width:
                    ray_idx = int(col_x / (self.width / num_rays))
                    if 0 <= ray_idx < num_rays:
                        # 벽과의 거리 체크: 벽이 스프라이트보다 멀리 있을 때만 렌더링
                        if rays[ray_idx]['distance'] > dist_x:
                            texture_x = col_x - draw_start_x
                            texture_x = max(0, min(sprite_width - 1, texture_x))
                            
                            # 1픽셀 두께의 세로 조각을 화면에 드로잉
                            screen.blit(
                                scaled_tex,
                                (col_x, draw_start_y),
                                (texture_x, 0, 1, sprite_height)
                            )
    
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
    
    def _render_wall_slice(self, screen, column_idx, column_width, ray, game_map=None):
        """벽 한 줄 그리기 (부드러운 음영)"""
        distance = ray['distance']
        wall_type = ray['wall_type']
        side = ray['side']
        map_x = ray.get('map_x')
        map_y = ray.get('map_y')
        
        if wall_type == 0:
            return
        
        # 벽 높이 계산
        wall_height = int(self.game_height / (distance + 0.0001))
        
        draw_start = max(0, self.half_height - wall_height // 2)
        draw_end = min(self.game_height, self.half_height + wall_height // 2)
        
        # 문 개방 진행률에 따른 슬라이드 효과 (천천히 열림)
        progress = 0.0
        if game_map and map_x is not None and map_y is not None:
            door_pos = (map_x, map_y)
            if door_pos in game_map.doors:
                progress = game_map.doors[door_pos].get('progress', 0.0)
                
        if progress > 0.0:
            draw_end_animated = draw_start + int(wall_height * (1.0 - progress))
            draw_end = min(draw_end, draw_end_animated)
            
        if draw_end <= draw_start:
            return
        
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
