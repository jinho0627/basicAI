"""
main.py
A팀: 메인 게임 엔진 - 모든 시스템 통합 및 게임 루프
(engine.py 통합 버전)
"""

import pygame
import sys
import math

# A팀 모듈
from player import Player
from raycaster import RayCaster
from renderer import Renderer

# B팀 모듈
from map import Map
from enemy import EnemyManager

# C팀 모듈
from game_systems import GameSystems


class GameEngine:
    """
    A+B+C 팀 코드를 통합하는 메인 게임 엔진
    초기화, 게임 루프, 이벤트 처리, 렌더링 담당
    """
    
    def __init__(self):
        """게임 엔진 초기화"""
        pygame.init()
        
        # 화면 설정
        self.width = 960
        self.height = 600
        self.hud_height = 80
        self.game_height = self.height - self.hud_height
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("DOOM Clone - Boogi-Man")
        
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # B팀: 맵 생성
        print("=== 맵 생성 중 ===")
        self.game_map = Map(width=21, height=21, seed=None)
        self.game_map.print_map()
        
        # A팀: 플레이어 생성
        px, py = self.game_map.player_spawn
        self.player = Player(px, py, angle=0)
        print(f"플레이어 스폰: ({px:.1f}, {py:.1f})")
        
        # A팀: 레이캐스터 & 렌더러
        self.raycaster = RayCaster(fov=math.pi / 2.5)  # 72도 FOV
        self.renderer = Renderer(self.width, self.height, self.hud_height)
        
        # B팀: 적 매니저
        self.enemy_manager = EnemyManager(difficulty='보통')
        self.enemy_manager.spawn_enemies(self.game_map)
        print(f"적 스폰 완료: {len(self.enemy_manager.enemies)}마리")
        
        # C팀: 게임 시스템
        self.game_systems = GameSystems()
        
        # 마우스 설정
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # 게임 상태
        self.running = True
        
        # FPS 표시
        self.font = pygame.font.SysFont("Courier New", 20)
        
        print("=== 게임 엔진 초기화 완료 ===\n")
    
    def reset_game(self):
        """게임 리셋 (재시작 시)"""
        # 맵 재생성
        self.game_map = Map(width=21, height=21, seed=None)
        
        # 플레이어 리스폰
        px, py = self.game_map.player_spawn
        self.player = Player(px, py, angle=0)
        
        # 적 재스폰
        self.enemy_manager.enemies.clear()
        self.enemy_manager.projectiles.clear()
        self.enemy_manager.spawn_enemies(self.game_map)
        
        print("=== 게임 리셋 완료 ===")
    
    def handle_events(self):
        """이벤트 처리 (키보드, 마우스, 종료)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # C팀 시작 화면 이벤트
            if self.game_systems.state == GameSystems.STATE_START:
                if self.game_systems.start_screen.handle_event(event):
                    self.game_systems.state = GameSystems.STATE_PLAYING
                    self.reset_game()
            
            # C팀 게임 오버 화면 이벤트
            elif self.game_systems.state == GameSystems.STATE_GAMEOVER:
                result = self.game_systems.gameover_screen.handle_event(event)
                if result == "restart":
                    self.game_systems._reset()
                    self.reset_game()
                elif result == "quit":
                    self.running = False
        
        # 플레이 중 마우스 회전
        if self.game_systems.state == GameSystems.STATE_PLAYING:
            mouse_rel = pygame.mouse.get_rel()
            self.player.handle_rotation(mouse_rel[0])
    
    def update(self, dt):
        """
        게임 로직 업데이트
        
        Parameters:
            dt (float): 델타 타임 (초 단위)
        """
        if self.game_systems.state != GameSystems.STATE_PLAYING:
            return
        
        dt_ms = int(dt * 1000)
        keys = pygame.key.get_pressed()
        
        # A팀: 플레이어 이동
        self.player.handle_movement(keys, dt, self.game_map)
        
        # B팀: 적 AI 업데이트
        player_pos = self.player.get_pos()
        self.enemy_manager.update_all(player_pos, self.game_map, dt)
        
        # B팀: 투사체 충돌 검사 → C팀 체력 감소
        damage = self.enemy_manager.check_projectile_hits(player_pos)
        if damage > 0:
            self.game_systems.health.take_damage(damage)
        
        # C팀: 시스템 업데이트 (무기, 체력, 점수)
        self.game_systems.update(dt_ms, keys)
        
        # 발사 처리 (C팀 → A팀 레이캐스트 → B팀 적)
        if self.game_systems.weapon.is_firing:
            self._handle_shooting()
    
    def _handle_shooting(self):
        """
        발사 시 레이캐스트로 적 충돌 판정
        C팀의 weapon.try_shoot() 후 호출됨
        """
        px, py = self.player.get_pos()
        angle = self.player.angle
        
        # 화면 중앙 광선 발사
        hit_info = self.raycaster._cast_single_ray(px, py, angle, self.game_map)
        
        # 적과의 거리 계산
        for enemy in self.enemy_manager.get_active_enemies():
            ex, ey = enemy.x, enemy.y
            
            # 플레이어 → 적 방향
            dx = ex - px
            dy = ey - py
            dist_to_enemy = math.sqrt(dx**2 + dy**2)
            
            # 각도 차이
            angle_to_enemy = math.atan2(dy, dx)
            angle_diff = abs(angle - angle_to_enemy)
            
            # 정규화 (0 ~ π)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            
            # 히트 판정 (각도 오차 ±0.2 라디안, 거리 체크)
            if angle_diff < 0.2 and dist_to_enemy < hit_info['distance'] + 0.5:
                damage = 30
                score_gained = enemy.take_damage(damage)
                
                if score_gained > 0:  # 적 사망
                    grade_type = "boss" if enemy.grade == 'F' else "normal"
                    self.game_systems.score.on_kill(grade_type)
                
                break  # 한 발에 하나만
    
    def render(self):
        """화면 렌더링"""
        gs = self.game_systems
        
        if gs.state == GameSystems.STATE_START:
            # C팀: 시작 화면
            gs.start_screen.draw(self.clock.get_time())
        
        elif gs.state == GameSystems.STATE_PLAYING:
            # A팀: 3D 게임 뷰
            px, py = self.player.get_pos()
            rays = self.raycaster.cast_rays(
                px, py, self.player.angle,
                self.width, self.game_map
            )
            
            enemies = self.enemy_manager.get_active_enemies()
            projectiles = self.enemy_manager.projectiles
            
            self.renderer.render_frame(
                self.screen, rays, px, py, self.player.angle,
                enemies, projectiles
            )
            
            # C팀: HUD 오버레이
            gs.draw()
            
            # FPS 표시
            fps_text = self.font.render(
                f"FPS: {int(self.clock.get_fps())}", 
                True, (255, 255, 0)
            )
            self.screen.blit(fps_text, (10, 10))
        
        elif gs.state == GameSystems.STATE_GAMEOVER:
            # C팀: 게임 오버 화면
            gs.gameover_screen.draw(gs.score.score, gs.score.kills, self.clock.get_time())
        
        pygame.display.flip()
    
    def run(self):
        """메인 게임 루프"""
        print("=== 게임 시작 ===")
        
        while self.running:
            # 델타 타임 계산 (초 단위)
            dt = self.clock.tick(self.target_fps) / 1000.0
            
            # 이벤트 처리
            self.handle_events()
            
            # 게임 로직 업데이트
            self.update(dt)
            
            # 화면 렌더링
            self.render()
        
        # 종료
        print("=== 게임 종료 ===")
        pygame.quit()
        sys.exit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  메인 진입점
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
