"""
game_systems.py
───────────────

의존: pygame  (pip install pygame)
사용: 팀원의 렌더러·맵·적 모듈과 연결
      game = GameSystems()   # 한 번만 생성
      game.run()             # 메인 루프 진입
"""

import pygame
import math
import random
import sys

# ────────────────────────────
#  상수
# ────────────────────────────
W, H        = 960, 600
FPS         = 60
TITLE       = "DOOM-LITE"

# 팔레트 (둠 느낌의 다크 + 핏빛 계열)
C_BLACK     = (0,   0,   0)
C_DARK      = (12,  12,  12)
C_DARKRED   = (100, 0,   0)
C_RED       = (200, 20,  20)
C_ORANGE    = (220, 100, 10)
C_YELLOW    = (240, 200, 30)
C_WHITE     = (255, 255, 255)
C_GRAY      = (120, 120, 120)
C_LTGRAY    = (180, 180, 180)
C_GREEN     = (40,  200, 60)
C_BLOOD     = (160, 0,   0)

# HUD 레이아웃
HUD_H       = 80          # 화면 하단 HUD 높이
GAME_H      = H - HUD_H  # 실제 게임 뷰 높이

# 체력
MAX_HP      = 100
# 탄약
MAX_AMMO    = 50
# 발사 쿨다운 (ms)
SHOOT_CD    = 250


# ────────────────────────────
#  사운드 생성기 (파일 없이 pygame synth)
# ────────────────────────────
class SoundEngine:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mixer.init()
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._build_sounds()

    def _sine_wave(self, freq: float, duration_ms: int,
                   vol: float = 0.6, decay: bool = True) -> pygame.mixer.Sound:
        import array, math
        sr = 44100
        n  = int(sr * duration_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t   = i / sr
            env = (1 - i / n) if decay else 1.0
            val = int(32767 * vol * env * math.sin(2 * math.pi * freq * t))
            buf.append(max(-32767, min(32767, val)))
        snd = pygame.mixer.Sound(buffer=buf)
        return snd

    def _noise_burst(self, duration_ms: int, vol: float = 0.5) -> pygame.mixer.Sound:
        import array
        sr  = 44100
        n   = int(sr * duration_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            env = 1 - i / n
            val = int(32767 * vol * env * random.uniform(-1, 1))
            buf.append(max(-32767, min(32767, val)))
        snd = pygame.mixer.Sound(buffer=buf)
        return snd

    def _build_sounds(self):
        # 총소리: 짧은 노이즈 + 낮은 사인
        self._cache["shoot"]   = self._noise_burst(80,  0.7)
        # 피격음
        self._cache["hit"]     = self._noise_burst(120, 0.5)
        # 사망
        self._cache["death"]   = self._sine_wave(80,  600, 0.8, True)
        # 아이템 획득
        self._cache["pickup"]  = self._sine_wave(880, 150, 0.5, False)
        # 메뉴 선택
        self._cache["select"]  = self._sine_wave(440, 100, 0.4, False)
        # 레벨업 / 점수 증가
        self._cache["score"]   = self._sine_wave(660, 120, 0.4, False)

    def play(self, name: str):
        snd = self._cache.get(name)
        if snd:
            snd.play()


# ────────────────────────────
#  총기 시스템
# ────────────────────────────
class Weapon:
    """
    총기 상태 관리 + 발사 애니메이션 좌표 반환
    팀원의 적 모듈과 연결:  weapon.shoot() → 충돌 판정은 팀원 코드에서
    """
    def __init__(self, sound: SoundEngine):
        self.snd        = sound
        self.ammo       = MAX_AMMO
        self.last_shot  = 0        # ms
        self.flash      = 0        # 발사 플래시 남은 시간 (ms)
        self.is_firing  = False

    # ── 외부 호출 ──────────────────
    def try_shoot(self) -> bool:
        """발사 가능하면 True 반환, 팀원 코드에서 ray-cast 처리"""
        now = pygame.time.get_ticks()
        if self.ammo <= 0:
            return False
        if now - self.last_shot < SHOOT_CD:
            return False
        self.ammo      -= 1
        self.last_shot  = now
        self.flash      = 90
        self.is_firing  = True
        self.snd.play("shoot")
        return True

    def add_ammo(self, n: int = 10):
        self.ammo = min(MAX_AMMO, self.ammo + n)
        self.snd.play("pickup")

    def update(self, dt: int):
        self.flash = max(0, self.flash - dt)
        if self.flash == 0:
            self.is_firing = False

    # ── HUD용 ─────────────────────
    @property
    def ammo_ratio(self) -> float:
        return self.ammo / MAX_AMMO


# ────────────────────────────
#  체력 시스템
# ────────────────────────────
class HealthSystem:
    def __init__(self, sound: SoundEngine):
        self.snd         = sound
        self.hp          = MAX_HP
        self.max_hp      = MAX_HP
        self._hit_flash  = 0   # 피격 화면 붉은 플래시 ms

    def take_damage(self, dmg: int):
        self.hp         = max(0, self.hp - dmg)
        self._hit_flash = 300
        self.snd.play("hit")

    def heal(self, n: int = 20):
        self.hp = min(self.max_hp, self.hp + n)
        self.snd.play("pickup")

    def is_dead(self) -> bool:
        return self.hp <= 0

    def update(self, dt: int):
        self._hit_flash = max(0, self._hit_flash - dt)

    # ── 화면 피격 오버레이 알파 ──
    @property
    def hit_alpha(self) -> int:
        return int(160 * self._hit_flash / 300)

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp


# ────────────────────────────
#  점수 시스템
# ────────────────────────────
class ScoreSystem:
    KILL_POINTS   = 100
    BONUS_STREAK  = 50    # 연속 킬 보너스

    def __init__(self, sound: SoundEngine):
        self.snd     = sound
        self.score   = 0
        self.kills   = 0
        self._streak = 0
        self._streak_timer = 0   # ms

    def on_kill(self, enemy_type: str = "normal"):
        multiplier = 2 if enemy_type == "boss" else 1
        base       = self.KILL_POINTS * multiplier
        bonus      = self.BONUS_STREAK * self._streak
        self.score += base + bonus
        self.kills += 1
        self._streak     += 1
        self._streak_timer = 3000   # 3초 안에 다음 킬 시 스트릭 유지
        self.snd.play("score")

    def update(self, dt: int):
        if self._streak_timer > 0:
            self._streak_timer -= dt
            if self._streak_timer <= 0:
                self._streak = 0

    @property
    def streak(self) -> int:
        return self._streak


# ────────────────────────────
#  HUD 렌더러
# ────────────────────────────
class HUD:
    """
    화면 하단 80px 영역에 HP / 탄약 / 점수 / 킬수 표시
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()
        self.font_lg = pygame.font.SysFont("Courier New", 28, bold=True)
        self.font_sm = pygame.font.SysFont("Courier New", 16, bold=True)
        self._flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # ── 내부 헬퍼 ─────────────────
    def _bar(self, x, y, w, h, ratio, filled_color, bg_color=C_DARK):
        pygame.draw.rect(self.screen, bg_color,      (x, y, w, h))
        pygame.draw.rect(self.screen, filled_color,  (x, y, int(w * ratio), h))
        pygame.draw.rect(self.screen, C_GRAY,         (x, y, w, h), 1)

    def _text(self, txt, font, color, x, y):
        surf = font.render(txt, True, color)
        self.screen.blit(surf, (x, y))

    # ── 메인 그리기 ───────────────
    def draw(self, health: HealthSystem, weapon: Weapon, score: ScoreSystem):
        s = self.screen
        hud_y = GAME_H

        # HUD 배경
        pygame.draw.rect(s, (18, 6, 6), (0, hud_y, W, HUD_H))
        pygame.draw.line(s, C_RED, (0, hud_y), (W, hud_y), 2)

        # ── 체력 ──
        self._text("HP", self.font_sm, C_RED, 20, hud_y + 10)
        hp_color = C_GREEN if health.hp_ratio > 0.4 else C_ORANGE if health.hp_ratio > 0.2 else C_RED
        self._bar(20, hud_y + 30, 160, 16, health.hp_ratio, hp_color)
        self._text(f"{health.hp}/{health.max_hp}", self.font_sm, C_WHITE, 20, hud_y + 50)

        # ── 탄약 ──
        self._text("AMMO", self.font_sm, C_ORANGE, 210, hud_y + 10)
        ammo_color = C_YELLOW if weapon.ammo_ratio > 0.3 else C_RED
        self._bar(210, hud_y + 30, 120, 16, weapon.ammo_ratio, ammo_color)
        self._text(f"{weapon.ammo}/{MAX_AMMO}", self.font_sm, C_WHITE, 210, hud_y + 50)

        # ── 점수 ──
        self._text("SCORE", self.font_sm, C_YELLOW, 370, hud_y + 10)
        self._text(f"{score.score:06d}", self.font_lg, C_WHITE, 370, hud_y + 30)

        # ── 킬 수 ──
        self._text("KILLS", self.font_sm, C_LTGRAY, 570, hud_y + 10)
        self._text(str(score.kills), self.font_lg, C_WHITE, 570, hud_y + 30)

        # ── 스트릭 ──
        if score.streak >= 2:
            streak_txt = f"x{score.streak} STREAK!"
            self._text(streak_txt, self.font_sm, C_ORANGE, 700, hud_y + 20)

        # ── 발사 플래시 (총구 섬광 효과) ──
        if weapon.is_firing:
            alpha = int(80 * weapon.flash / 90)
            flash = pygame.Surface((W, GAME_H), pygame.SRCALPHA)
            flash.fill((255, 200, 50, alpha))
            s.blit(flash, (0, 0))

        # ── 피격 화면 ──
        if health.hit_alpha > 0:
            self._flash_surf.fill((200, 0, 0, health.hit_alpha))
            s.blit(self._flash_surf, (0, 0))


# ────────────────────────────
#  시작 화면
# ────────────────────────────
class StartScreen:
    def __init__(self, screen: pygame.Surface, sound: SoundEngine):
        self.screen = screen
        self.snd    = sound
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Courier New", 72, bold=True)
        self.font_sub   = pygame.font.SysFont("Courier New", 22, bold=True)
        self.font_sm    = pygame.font.SysFont("Courier New", 16)
        self._tick = 0

    def handle_event(self, event) -> bool:
        """ENTER / SPACE 누르면 True 반환 → 게임 시작"""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.snd.play("select")
                return True
        return False

    def draw(self, dt: int):
        s = self._tick
        self._tick += dt
        scr = self.screen

        # 배경: 검정 + 혈흔 느낌의 그라데이션 라인
        scr.fill(C_BLACK)
        for i in range(0, W, 40):
            alpha = 60 + 40 * math.sin(i * 0.05 + self._tick * 0.001)
            pygame.draw.line(scr, (int(alpha), 0, 0), (i, 0), (i, H))

        # 타이틀
        blink_alpha = int(200 + 55 * math.sin(self._tick * 0.004))
        title_surf  = self.font_title.render(TITLE, True, C_RED)
        # 글로우 효과 (오프셋 그림자)
        for ox, oy in [(-3,3),(3,-3),(-3,-3),(3,3)]:
            shadow = self.font_title.render(TITLE, True, C_DARKRED)
            scr.blit(shadow, (W//2 - shadow.get_width()//2 + ox,
                              H//3 - shadow.get_height()//2 + oy))
        scr.blit(title_surf, (W//2 - title_surf.get_width()//2, H//3 - title_surf.get_height()//2))

        # 서브타이틀
        sub = self.font_sub.render("SURVIVE. SHOOT. SCORE.", True, C_ORANGE)
        scr.blit(sub, (W//2 - sub.get_width()//2, H//2))

        # 시작 안내 (깜빡)
        if (self._tick // 500) % 2 == 0:
            prompt = self.font_sub.render("PRESS  ENTER  TO  START", True, C_WHITE)
            scr.blit(prompt, (W//2 - prompt.get_width()//2, H*2//3))

        # 조작법
        controls = [
            "WASD / ARROW  :  이동",
            "MOUSE / LEFT  :  발사",
            "ESC           :  종료",
        ]
        for i, line in enumerate(controls):
            surf = self.font_sm.render(line, True, C_GRAY)
            scr.blit(surf, (W//2 - surf.get_width()//2, H*3//4 + i * 22))


# ────────────────────────────
#  종료(게임 오버) 화면
# ────────────────────────────
class GameOverScreen:
    def __init__(self, screen: pygame.Surface, sound: SoundEngine):
        self.screen   = screen
        self.snd      = sound
        self.font_big = pygame.font.SysFont("Courier New", 64, bold=True)
        self.font_med = pygame.font.SysFont("Courier New", 28, bold=True)
        self.font_sm  = pygame.font.SysFont("Courier New", 18)
        self._tick    = 0
        self._played  = False   # 사망 사운드 한 번만

    def reset(self):
        self._tick   = 0
        self._played = False

    def handle_event(self, event) -> str:
        """'R' → 'restart', ESC → 'quit'"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.snd.play("select")
                return "restart"
            if event.key == pygame.K_ESCAPE:
                return "quit"
        return ""

    def draw(self, score: int, kills: int, dt: int):
        self._tick += dt
        if not self._played:
            self.snd.play("death")
            self._played = True

        scr = self.screen
        # 배경 점진 어둠
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        alpha   = min(200, int(self._tick * 0.2))
        overlay.fill((0, 0, 0, alpha))
        scr.blit(overlay, (0, 0))

        # GAME OVER 텍스트
        go = self.font_big.render("GAME  OVER", True, C_RED)
        scr.blit(go, (W//2 - go.get_width()//2, H//4))

        # 결과
        sc_surf = self.font_med.render(f"SCORE  :  {score:06d}", True, C_YELLOW)
        kl_surf = self.font_med.render(f"KILLS  :  {kills}",     True, C_WHITE)
        scr.blit(sc_surf, (W//2 - sc_surf.get_width()//2, H//2 - 30))
        scr.blit(kl_surf, (W//2 - kl_surf.get_width()//2, H//2 + 20))

        # 안내
        if (self._tick // 600) % 2 == 0:
            hint = self.font_sm.render("[R] RESTART    [ESC] QUIT", True, C_LTGRAY)
            scr.blit(hint, (W//2 - hint.get_width()//2, H*3//4))


# ────────────────────────────
#  GameSystems  (메인 조립체)
# ────────────────────────────
class GameSystems:
    """
    팀원 코드에서 import 후 아래 API를 사용하세요:

        gs = GameSystems()

        # 메인 루프에서
        dt = clock.tick(FPS)
        gs.update(dt, keys)

        # 적이 맞았을 때
        gs.score.on_kill("normal")

        # 플레이어가 피격됐을 때
        gs.health.take_damage(20)

        # 발사 시도 (bool 반환)
        fired = gs.weapon.try_shoot()

        # 그리기 (게임 뷰를 먼저 그린 뒤 호출)
        gs.draw()
    """
    STATE_START    = "start"
    STATE_PLAYING  = "playing"
    STATE_GAMEOVER = "gameover"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        self.sound  = SoundEngine()
        self.weapon = Weapon(self.sound)
        self.health = HealthSystem(self.sound)
        self.score  = ScoreSystem(self.sound)
        self.hud    = HUD(self.screen)

        self.start_screen    = StartScreen(self.screen, self.sound)
        self.gameover_screen = GameOverScreen(self.screen, self.sound)

        self.state = self.STATE_START

    # ── 리셋 ──────────────────────
    def _reset(self):
        self.weapon  = Weapon(self.sound)
        self.health  = HealthSystem(self.sound)
        self.score   = ScoreSystem(self.sound)
        self.hud     = HUD(self.screen)
        self.gameover_screen.reset()
        self.state   = self.STATE_PLAYING

    # ── 외부 API ──────────────────
    def update(self, dt: int, keys):
        """매 프레임 호출. keys = pygame.key.get_pressed()"""
        if self.state == self.STATE_PLAYING:
            self.weapon.update(dt)
            self.health.update(dt)
            self.score.update(dt)

            # 마우스 클릭 또는 왼쪽 Ctrl 발사
            if (pygame.mouse.get_pressed()[0] or keys[pygame.K_LCTRL]):
                self.weapon.try_shoot()

            if self.health.is_dead():
                self.state = self.STATE_GAMEOVER

    def draw(self):
        """플레이 중: HUD + 오버레이 그리기 (팀원 게임 뷰 위에 덮음)"""
        if self.state == self.STATE_PLAYING:
            self.hud.draw(self.health, self.weapon, self.score)

    # ── 독립 실행 데모 루프 ────────
    def run(self):
        """
        팀원 모듈 없이 단독 테스트용 메인 루프.
        실제 통합 시에는 팀원 메인 루프에서 update() / draw() 만 호출하세요.
        """
        while True:
            dt    = self.clock.tick(FPS)
            keys  = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if self.state == self.STATE_START:
                    if self.start_screen.handle_event(event):
                        self.state = self.STATE_PLAYING

                elif self.state == self.STATE_GAMEOVER:
                    result = self.gameover_screen.handle_event(event)
                    if result == "restart":
                        self._reset()
                    elif result == "quit":
                        pygame.quit(); sys.exit()

            # ── 상태별 업데이트 & 드로우 ──
            if self.state == self.STATE_START:
                self.start_screen.draw(dt)

            elif self.state == self.STATE_PLAYING:
                # ── 데모용 임시 배경 (팀원 뷰로 교체) ──
                self.screen.fill((20, 20, 20))
                _demo_draw_placeholder(self.screen, self.weapon)
                # ── 여기까지가 팀원 코드 영역 ──

                self.update(dt, keys)
                self.draw()

                # 데모: 키보드로 테스트
                _demo_handle_keys(keys, self)

            elif self.state == self.STATE_GAMEOVER:
                # 배경 유지 (마지막 게임 뷰 위에 오버레이)
                self.gameover_screen.draw(self.score.score, self.score.kills, dt)

            pygame.display.flip()


# ────────────────────────────
#  데모 헬퍼 (단독 실행 테스트용)
# ────────────────────────────
_demo_enemy_tick = 0

def _demo_draw_placeholder(screen: pygame.Surface, weapon: Weapon):
    """팀원의 3D 뷰 대신 임시 화면"""
    font = pygame.font.SysFont("Courier New", 18)
    msg  = font.render("[팀원 3D 뷰 영역 — 여기에 레이캐스터 삽입]", True, (80, 80, 80))
    screen.blit(msg, (W//2 - msg.get_width()//2, GAME_H//2 - 10))

    if weapon.is_firing:
        # 간단 총구 표시
        pygame.draw.line(screen, C_YELLOW, (W//2, GAME_H), (W//2, GAME_H - 80), 4)
        pygame.draw.circle(screen, C_WHITE, (W//2, GAME_H - 90), 10)


def _demo_handle_keys(keys, gs: "GameSystems"):
    """데모: 숫자 키로 이벤트 시뮬레이션"""
    global _demo_enemy_tick
    _demo_enemy_tick += 1
    if _demo_enemy_tick % (FPS * 2) == 0:        # 2초마다 자동 피격
        gs.health.take_damage(random.randint(5, 20))
    if _demo_enemy_tick % (FPS * 3) == 0:         # 3초마다 자동 킬
        gs.score.on_kill()


# ────────────────────────────
#  진입점
# ────────────────────────────
if __name__ == "__main__":
    gs = GameSystems()
    gs.run()
