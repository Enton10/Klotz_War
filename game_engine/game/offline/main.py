"""
Offline-Modus für die Klotz-War Game Engine.

Struktur:
    - Konstanten
    - Hilfsklassen (Snake, SaveZone, Wechsler, Button)
    - UI-Hilfsfunktionen (_grid)
    - Menüs (menu_spielerzahl, winner_screen)
    - Spiel-Loop (play_game)
    - Einstieg (main)
"""

import math
import random
import time

import pygame


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1900, 1000
BG_COLOR = (15, 15, 30)
GRID_COLOR = (25, 25, 50)

# Safe-Zone Schutzdauer in Millisekunden
SAVE_LIMIT_MS = 200

# Globale Render-Kontexte (werden von main() gesetzt)
screen = None
clock = None
font_big = None
font_mid = None
font_small = None
CTX = None
save_zones_size = (100,100)

# ---------------------------------------------------------------------------
# Spieler-Schlange
# ---------------------------------------------------------------------------
class Snake:
    def __init__(self, name, start_pos, color, eyes_color, controls,
                 level=0, size=20):
        self.name = name
        self.color = color
        self.eyes_color = eyes_color
        self.base_color = color
        self.size = size
        self.controls = controls
        self.level = level
        self.rect = pygame.Rect(start_pos[0], start_pos[1], size, size)
        self.speed = 5
        self.trail = []
        self.max_trail = 18
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_max = 50

        # Zeitpunkt (ms) ab dem die Schlange geschützt ist
        self.save_since = 0

    # -- Input / Bewegung -------------------------------------------------
    def handle_input(self, keys):
        if not self.alive or self.dying:
            return
        c = self.controls
        if keys[c["left"]]:
            self.rect.x -= self.speed
        if keys[c["right"]]:
            self.rect.x += self.speed
        if keys[c["up"]]:
            self.rect.y -= self.speed
        if keys[c["down"]]:
            self.rect.y += self.speed
        self.rect.x = max(0, min(SCREEN_W - self.size, self.rect.x))
        self.rect.y = max(0, min(SCREEN_H - self.size, self.rect.y))

    def update_trail(self):
        if not self.alive or self.dying:
            return
        self.trail.append((self.rect.x, self.rect.y, self.size))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

    def grow(self, factor=1.5):
        center = self.rect.center
        self.size = int(self.size * factor)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = center
        self.max_trail = int(self.max_trail * factor)

    def start_death(self):
        self.dying = True
        self.death_timer = 0

    # -- Rendering --------------------------------------------------------
    def draw(self, surface):
        if not self.alive and not self.dying:
            return
        for i, (tx, ty, ts) in enumerate(self.trail):
            alpha = int(80 + (i / max(1, len(self.trail))) * 150)
            c = (min(self.color[0], 255),
                 min(self.color[1], 255),
                 min(self.color[2], 255))
            s = pygame.Surface((ts, ts), pygame.SRCALPHA)
            s.fill((c[0], c[1], c[2], alpha))
            surface.blit(s, (tx, ty))

        if self.dying:
            t = self.death_timer / self.death_max
            radius = int(self.size * (1 + t * 200))
            alpha = max(0, int(255 * (1 - t)))
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 50, 50, alpha),
                               (radius, radius), radius)
            surface.blit(s, (self.rect.centerx - radius,
                             self.rect.centery - radius))
            for _ in range(3):
                px = self.rect.centerx + random.randint(-radius, radius)
                py = self.rect.centery + random.randint(-radius, radius)
                pygame.draw.circle(surface, (255, 200, 0), (px, py),
                                   random.randint(2, 5))
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            ex = self.rect.x + self.size // 4
            ey = self.rect.y + self.size // 4
            pygame.draw.circle(surface, self.eyes_color,
                               (ex, ey), max(2, self.size // 8))
            pygame.draw.circle(surface, self.eyes_color,
                               (ex + self.size // 2, ey),
                               max(2, self.size // 8))

    # -- Kollision / Save-Zone -------------------------------------------
    def collides_with(self, other):
        if not (self.alive and other.alive) or self.dying or other.dying:
            return False
        dx = self.rect.centerx - other.rect.centerx
        dy = self.rect.centery - other.rect.centery
        return math.hypot(dx, dy) < (self.size + other.size) / 2

    def set_save(self):
        self.save_since = time.time() * 1000

    def is_save(self):
        return (time.time() * 1000 - self.save_since) <= SAVE_LIMIT_MS


# ---------------------------------------------------------------------------
# Safe-Zone
# ---------------------------------------------------------------------------
class SaveZone:
    def __init__(self, name, color, size):
        self.name = name
        self.color = color
        self.size = size
        self.zone = pygame.Surface(size, pygame.SRCALPHA)
        self.active = False
        self.show_timer = 0

        pos_x = random.randint(0, SCREEN_W - size[0])
        pos_y = random.randint(0, SCREEN_H - size[1])
        self.rect = pygame.Rect(pos_x, pos_y, size[0], size[1])

    def draw_savezone(self, surface):
        if not self.active:
            self.show_timer += 1
            if self.show_timer > 110:
                self.active = True
                self.show_timer = 0
        if self.active:
            self.zone.fill((self.color[0], self.color[1], self.color[2], 100))
            surface.blit(self.zone, self.rect)


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, rect, text, color=(60, 120, 200),
                 hover=(90, 160, 240)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, surface, mouse_pos):
        c = self.hover if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=14)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3,
                         border_radius=14)
        label = font_mid.render(self.text, True, (255, 255, 255))
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ---------------------------------------------------------------------------
# Wechsler (Power-Up)
# ---------------------------------------------------------------------------
class Wechsler:
    def __init__(self):
        self.rect = pygame.Rect(-100, -100, 20, 20)
        self.active = False
        self.timer = 0

    def update(self):
        self.timer += 1
        if not self.active and self.timer > 240:
            self.spawn()

    def spawn(self):
        self.rect.x = random.randint(50, SCREEN_W - 70)
        self.rect.y = random.randint(50, SCREEN_H - 70)
        self.active = True
        self.timer = 0

    def consume(self):
        self.active = False
        self.timer = 0
        self.rect.x = -100
        self.rect.y = -100

    def draw(self, surface):
        if self.active:
            r = 12 + int(4 * math.sin(pygame.time.get_ticks() / 150))
            pygame.draw.circle(surface, (0, 230, 230), self.rect.center, r)
            pygame.draw.circle(surface, (255, 255, 255),
                               self.rect.center, r, 2)


# ---------------------------------------------------------------------------
# UI-Hilfen
# ---------------------------------------------------------------------------
def _grid():
    screen.fill(BG_COLOR)
    for i in range(0, SCREEN_W, 40):
        pygame.draw.line(screen, GRID_COLOR, (i, 0), (i, SCREEN_H))
    for i in range(0, SCREEN_H, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, i), (SCREEN_W, i))


# ---------------------------------------------------------------------------
# Menüs
# ---------------------------------------------------------------------------
def menu_spielerzahl():
    """
    Zeigt erst Gamemode-Auswahl, dann Spielerzahl-Auswahl.
    Gibt (anzahl, gamemode) zurück oder None bei Abbruch.
    """
    title = font_big.render("Normal", True, (255, 255, 255))
    subtitle = font_small.render("Was willst du spielen", True,
                                 (200, 200, 200))

    btn_normal = Button((SCREEN_W // 2 - 200, 350, 400, 90), "Normal")
    btn_1vs2 = Button((SCREEN_W // 2 - 200, 450, 400, 90), "1 vs. 2")
    btn_2 = Button((SCREEN_W // 2 - 200, 550, 400, 90), "2")
    btn_quit = Button((SCREEN_W // 2 - 200, 710, 400, 90), "Beenden",
                      color=(150, 50, 50), hover=(200, 70, 70))

    btn_s1 = Button((SCREEN_W // 2 - 200, 350, 400, 90), "1 Spieler")
    btn_s2 = Button((SCREEN_W // 2 - 200, 450, 400, 90), "2 Spieler")
    btn_s3 = Button((SCREEN_W // 2 - 200, 550, 400, 90), "3 Spieler")

    # --- Phase 1: Gamemode-Auswahl ---------------------------------------
    gamemode = None
    while gamemode is None:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn_normal.clicked(p):
                    gamemode = "Normal"
                elif btn_1vs2.clicked(p):
                    return 3, "1 vs. 2"
                elif btn_2.clicked(p):
                    gamemode = "2"
                elif btn_quit.clicked(p):
                    return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    gamemode = "Normal"
                elif event.key == pygame.K_2:
                    gamemode = "Extra"
                elif event.key == pygame.K_3:
                    gamemode = "2"
                elif event.key == pygame.K_ESCAPE:
                    return None

        _grid()
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 320)))
        btn_normal.draw(screen, mouse_pos)
        btn_1vs2.draw(screen, mouse_pos)
        btn_2.draw(screen, mouse_pos)
        btn_quit.draw(screen, mouse_pos)
        CTX.present()
        clock.tick(60)

    # --- Phase 2: Spielerzahl --------------------------------------------
    info = [
        "Spieler 1 (blau):  Pfeiltasten",
        "Spieler 2 (grün):  W A S D",
        "Spieler 3 (gelb):  I J K L",
        "Wenn zwei Schlangen kollidieren, stirbt die mit dem kleineren Level.",
        "Der Sieger wächst um 50%. Letzte Schlange gewinnt!",
    ]
    while True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn_s1.clicked(p):
                    return 1, gamemode
                if btn_s2.clicked(p):
                    return 2, gamemode
                if btn_s3.clicked(p):
                    return 3, gamemode
                if btn_quit.clicked(p):
                    return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1, gamemode
                if event.key == pygame.K_2:
                    return 2, gamemode
                if event.key == pygame.K_3:
                    return 3, gamemode
                if event.key == pygame.K_ESCAPE:
                    return None

        _grid()
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 320)))
        btn_s1.draw(screen, mouse_pos)
        btn_s2.draw(screen, mouse_pos)
        btn_s3.draw(screen, mouse_pos)
        btn_quit.draw(screen, mouse_pos)
        for i, line in enumerate(info):
            t = font_small.render(line, True, (180, 180, 200))
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 850 + i * 30)))
        CTX.present()
        clock.tick(60)


def winner_screen(winner_name, winner_color, snakes, gamemode):
    """
    Gewinner-Bildschirm.
    Rückgabe:
        True  -> zurück ins Menü
        False -> Programm beenden
        ("again", n, gm) -> Spiel mit n Spielern erneut starten
    """
    btn_again = Button((SCREEN_W // 2 - 200, 600, 400, 90), "Nochmal")
    btn_menu = Button((SCREEN_W // 2 - 200, 700, 400, 90),
                      "Zurück zum Menü")

    while True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn_menu.clicked(p):
                    return True
                if btn_again.clicked(p):
                    return ("again", len(snakes), gamemode)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    return ("again", len(snakes), gamemode)

        _grid()
        title = font_big.render("🏆 Gewinner!", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 300)))
        name_surf = font_big.render(f"{winner_name}", True, winner_color)
        screen.blit(name_surf,
                    name_surf.get_rect(center=(SCREEN_W // 2, 450)))
        sub = font_mid.render("hat das Spiel gewonnen!", True,
                              (220, 220, 220))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 560)))
        btn_again.draw(screen, mouse_pos)
        btn_menu.draw(screen, mouse_pos)
        CTX.present()
        clock.tick(60)


# ---------------------------------------------------------------------------
# Spielablauf
# ---------------------------------------------------------------------------
def _make_snakes(num_players, gamemode):
    if gamemode == "1 vs. 2":
        eyes = [(255, 255, 255), (255, 0, 0), (0, 255, 0)]
        colors = [(255, 0, 0), (0, 0, 255), (0, 0, 255)]
    else:
        eyes = [(255, 255, 255)] * 3
        colors = [(255, 55, 0), (55, 0, 255), (0, 255, 55)]

    layouts = [
        ("Spieler 1", (SCREEN_W - 100, SCREEN_H - 100),
         {"up": pygame.K_UP, "down": pygame.K_DOWN,
          "left": pygame.K_LEFT, "right": pygame.K_RIGHT}),
        ("Spieler 2", (50, 50),
         {"up": pygame.K_w, "down": pygame.K_s,
          "left": pygame.K_a, "right": pygame.K_d}),
        ("Spieler 3", (SCREEN_W // 2, SCREEN_H // 2),
         {"up": pygame.K_i, "down": pygame.K_k,
          "left": pygame.K_j, "right": pygame.K_l}),
    ]

    snakes = []
    for i in range(num_players):
        name, pos, ctrl = layouts[i]
        snakes.append(Snake(name, pos, colors[i], eyes[i], ctrl))
    return snakes


def play_game(num_players, gamemode, surface):
    print(f"Starte Spiel: {num_players} Spieler – Modus: {gamemode}")

    snakes = _make_snakes(num_players, gamemode)
    save_zones = [SaveZone("Zone1", (200, 200, 200), save_zones_size)]
    wechsler = Wechsler()
    winner = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_ESCAPE:
                return True

        # --- Input -----------------------------------------------------
        keys = pygame.key.get_pressed()
        for s in snakes:
            s.handle_input(keys)
            s.update_trail()

        # --- Wechsler --------------------------------------------------
        wechsler.update()
        if wechsler.active:
            for s in snakes:
                if (s.alive and not s.dying
                        and s.rect.colliderect(wechsler.rect)):
                    if random.randint(1, 2) == 1:
                        s.speed += 1
                    else:
                        s.grow(1.2)
                    s.level += 1
                    wechsler.consume()
                    break

        # --- Kollisionen ----------------------------------------------
        alive_snakes = [s for s in snakes if s.alive and not s.dying]
        for i in range(len(alive_snakes)):
            for j in range(i + 1, len(alive_snakes)):
                a, b = alive_snakes[i], alive_snakes[j]
                if not a.collides_with(b):
                    continue

                # Team-Modus: Spieler 2 + 3 sind verbündet
                if gamemode == "1 vs. 2":
                    teammates = {"Spieler 2", "Spieler 3"}
                    if a.name in teammates and b.name in teammates:
                        continue

                if a.level > b.level:
                    if b.is_save():
                        continue
                    loser, winner_snake = b, a
                elif a.level < b.level:
                    if a.is_save():
                        continue
                    loser, winner_snake = a, b
                else:
                    continue  # Gleichstand: kein Schaden

                loser.start_death()
                winner_snake.grow(3.5)
                print(f"{winner_snake.name} hat {loser.name} besiegt!")

        # --- Safe-Zone Eintritt ---------------------------------------
        for z in save_zones:
            if not z.active:
                continue
            for q in alive_snakes:
                if z.rect.collidepoint(q.rect.center) and not q.is_save():
                    print(f"{q.name} hat die Save-Zone betreten")
                    q.set_save()

        # --- Todes-Animation ------------------------------------------
        for s in snakes:
            if s.dying:
                s.death_timer += 1
                if s.death_timer >= s.death_max:
                    s.dying = False
                    s.alive = False

        # --- Spielende-Bedingung --------------------------------------
        living = [s for s in snakes if s.alive]
        dying_now = [s for s in snakes if s.dying]

        if gamemode == "1 vs. 2" and dying_now:
            if dying_now[0].name == "Spieler 1":
                return winner_screen("Team Blau", (55, 0, 255),
                                     snakes, gamemode)

        if num_players != 1:
            if len(living) <= 1 and not dying_now:
                winner = living[0] if living else None
                running = False
        else:
            if len(living) == 0 and not dying_now:
                running = False

        # --- Render ---------------------------------------------------
        _grid()
        wechsler.draw(screen)
        for s in snakes:
            s.draw(screen)
        for z in save_zones:
            z.draw_savezone(surface=screen)

        for idx, s in enumerate(snakes):
            if not s.alive and not s.dying:
                status = "TOT"
            else:
                status = f"Größe {s.size}"
            txt = font_small.render(
                f"{s.name}: {status}  Level: {s.level}",
                True, s.base_color)
            screen.blit(txt, (20, 20 + idx * 32))

        CTX.present()
        clock.tick(60)

    if winner:
        return winner_screen(winner.name, winner.base_color,
                             snakes, gamemode)
    return winner_screen("Niemand", (200, 200, 200), snakes, gamemode)


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------
def main(ctx):
    global screen, clock, font_big, font_mid, font_small, CTX
    CTX = ctx
    screen = ctx.surf
    clock = ctx.clock
    font_big = ctx.font_big
    font_mid = ctx.font_mid
    font_small = ctx.font_small

    while True:
        selection = menu_spielerzahl()
        if selection is None:
            return None
        choice, gamemode = selection

        result = play_game(choice, gamemode, surface=screen)

        # Schleife für "Nochmal"
        while isinstance(result, tuple) and result and result[0] == "again":
            _, n, gm = result
            result = play_game(n, gm, surface=screen)

        # False = beenden, True = zurück ins Menü
        if result is False:
            return gamemode


# ---------------------------------------------------------------------------
# Standalone Dev-Modus
# ---------------------------------------------------------------------------
class _DevCtx:
    def __init__(self):
        pygame.init()
        self.surf = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arial", 72, bold=True)
        self.font_mid = pygame.font.SysFont("arial", 42, bold=True)
        self.font_small = pygame.font.SysFont("arial", 28)
        self.W, self.H, self.scale = SCREEN_W, SCREEN_H, 1.0

    def present(self):
        pygame.display.flip()

    def map(self, pos):
        return pos

    def mouse(self):
        return pygame.mouse.get_pos()


if __name__ == "__main__":
    main(_DevCtx())
    pygame.quit()
