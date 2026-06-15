"""
메인 진입점: A팀 + B팀 + C팀 완전 통합
"""

import pygame
import sys
import math

# A팀
from player import Player
from raycaster import RayCaster
from renderer import Renderer

# B팀
from map import Map
from enemy import EnemyManager

# C팀
from game_systems import GameSystems


class IntegratedGame:
    """A+B+C 팀 코드 통합 게임 엔진"""
    
    def __init__(self):
        pygame.init()
        
        # C팀 시스템 초기화
        self.game_systems = GameSystems()
        self.screen = self.game_systems.screen
        self.clock = self.game_systems.clock
        
        # 화면 설정
        self.width = 960
        self.height = 600
        self.hud_height = 80
        self.game_height = self.height - self.hud_height
        
        # B팀 맵 생성
        self.game_map = Map(width=21, height=21, seed=None)
        print("=== 맵 생성 완료 ===")
        self.game_map.print_map()
        
        # A팀 플레이어 생성
        px, py = self.game_map.player_spawn
        self.player = Player(px, py, angle=0)
        
        # A팀 레이캐스터 & 렌더러
        self.raycaster = RayCaster(fov=math.pi / 3)
        self.renderer = Renderer(self.width, self.height, self.hud_height)
        
        # B팀 적 매니저
        self.enemy_manager = EnemyManager(difficulty='보통')
        self.enemy_manager.spawn_enemies(self.game_map)
        
        # 마우스 설정
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # FPS 표시
        self.font = pygame.font.SysFont("Courier New", 20)
        
    def reset_game(self):
        """게임 리셋 (C팀 restart 호출 시)"""
        # 맵 재생성
        self.game_map = Map(width=21, height=21, seed=None)
        self.game_map.print_map()
        
        # 플레이어 리스폰
        px, py = self.game_map.player_spawn
        self.player = Player(px, py, angle=0)
        
        # 적 재스폰
        self.enemy_manager.spawn_enemies(self.game_map)
        
    def handle_events(self):
        """이벤트 처리 (C팀 상태에 따라 분기)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # C팀 시작 화면
            if self.game_systems.state == GameSystems.STATE_START:
                if self.game_systems.start_screen.handle_event(event):
                    self.game_systems.state = GameSystems.STATE_PLAYING
                    self.reset_game()  # 게임 시작 시 초기화
            
            # C팀 게임 오버 화면
            elif self.game_systems.state == GameSystems.STATE_GAMEOVER:
                result = self.game_systems.gameover_screen.handle_event(event)
                if result == "restart":
                    self.game_systems._reset()
                    self.reset_game()
                elif result == "quit":
                    pygame.quit()
                    sys.exit()
        
        # 마우스 회전 (플레이 중에만)
        if self.game_systems.state == GameSystems.STATE_PLAYING:
            mouse_rel = pygame.mouse.get_rel()
            self.player.handle_rotation(mouse_rel[0])
    
    def update(self, dt_sec):
        """게임 로직 업데이트"""
        if self.game_systems.state != GameSystems.STATE_PLAYING:
            return
        
        dt_ms = int(dt_sec * 1000)
        keys = pygame.key.get_pressed()
        
        # A팀: 플레이어 이동
        self.player.handle_movement(keys, dt_sec, self.game_map)
        
        # B팀: 적 AI 업데이트
        player_pos = self.player.get_pos()
        self.enemy_manager.update_all(player_pos, self.game_map, dt_sec)
        
        # B팀: 투사체 충돌 검사 → C팀 체력 연동
        damage = self.enemy_manager.check_projectile_hits(player_pos)
        if damage > 0:
            self.game_systems.health.take_damage(damage)
        
        # C팀: 시스템 업데이트 (무기, 체력, 점수)
        self.game_systems.update(dt_ms, keys)
        
        # 발사 처리 (C팀 weapon.try_shoot() → A팀 레이캐스트 충돌)
        if self.game_systems.weapon.is_firing:
            self._handle_shooting()
    
    def _handle_shooting(self):
        """발사 시 적 충돌 판정 (레이캐스트)"""
        px, py = self.player.get_pos()
        angle = self.player.angle
        
        # 화면 중앙 광선 발사
        hit_info = self.raycaster._cast_single_ray(px, py, angle, self.game_map)
        
        # 적과의 거리 계산
        for enemy in self.enemy_manager.get_active_enemies():
            ex, ey = enemy.x, enemy.y
            
            # 플레이어 → 적 방향 벡터
            dx = ex - px
            dy = ey - py
            dist_to_enemy = math.sqrt(dx**2 + dy**2)
            
            # 각도 차이 계산
            angle_to_enemy = math.atan2(dy, dx)
            angle_diff = abs(angle - angle_to_enemy)
            
            # 정규화 (0 ~ π)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            
            # 히트 판정 (각도 오차 ±0.1 라디안, 거리 레이캐스트 거리 이내)
            if angle_diff < 0.1 and dist_to_enemy < hit_info['distance'] + 0.5:
                # 적 피격
                damage = 30  # 총 데미지
                score_gained = enemy.take_damage(damage)
                
                if score_gained > 0:  # 적 사망
                    # C팀 점수 증가
                    grade_type = "boss" if enemy.grade == 'F' else "normal"
                    self.game_systems.score.on_kill(grade_type)
                
                break  # 한 발에 하나만
    
    def render(self):
        """화면 렌더링"""
        gs = self.game_systems
        
        # 상태별 렌더링
        if gs.state == GameSystems.STATE_START:
            # C팀 시작 화면
            gs.start_screen.draw(self.clock.get_time())
        
        elif gs.state == GameSystems.STATE_PLAYING:
            # A팀: 3D 게임 뷰 렌더링
            px, py = self.player.get_pos()
            rays = self.raycaster.cast_rays(
                px, py, self.player.angle,
                self.width, self.game_map
            )
            
            enemies = self.enemy_manager.get_active_enemies()
            projectiles = self.enemy_manager.projectiles
            
            self.renderer.render_frame(self.screen, rays, enemies, projectiles)
            
            # C팀: HUD 오버레이
            gs.draw()
            
            # FPS 표시
            fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))
        
        elif gs.state == GameSystems.STATE_GAMEOVER:
            # 마지막 게임 뷰 유지
            # C팀 게임 오버 오버레이
            gs.gameover_screen.draw(gs.score.score, gs.score.kills, self.clock.get_time())
        
        pygame.display.flip()
    
    def run(self):
        """메인 게임 루프"""
        while True:
            dt = self.clock.tick(60) / 1000.0  # 초 단위
            
            self.handle_events()
            self.update(dt)
            self.render()


if __name__ == "__main__":
    game = IntegratedGame()
    game.run()