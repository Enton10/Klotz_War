from operator import le
import random, math, pygame
from random import choice

SCREEN_W, SCREEN_H = 1900, 1000
BG_COLOR = (15, 15, 30)

screen = clock = font_big = font_mid = font_small = CTX = None



class Snake:
    def __init__(self, name, start_pos, color, eyes_color, controls, level=0, size=20):
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
        self.max_trail = 5
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_max = 50

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

    def draw(self, surface):
        if not self.alive and not self.dying:
            return
        for i, (tx, ty, ts) in enumerate(self.trail):
            alpha = int(80 + (i / max(1, len(self.trail))) * 150)
            c = (min(self.color[0], 255), min(self.color[1], 255),
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
            #Augen
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            ex = self.rect.x + self.size // 4
            ey = self.rect.y + self.size // 4
            pygame.draw.circle(surface, self.eyes_color,
                               (ex, ey), max(2, self.size // 8))
            pygame.draw.circle(surface, self.eyes_color,
                               (ex + self.size // 2, ey),
                               max(2, self.size // 8))

    def collides_with(self, other):
        if not (self.alive and other.alive) or self.dying or other.dying:
            return False
        dx = self.rect.centerx - other.rect.centerx
        dy = self.rect.centery - other.rect.centery
        return math.hypot(dx, dy) < (self.size + other.size) / 2


class Button:
    def __init__(self, rect, text, color=(60, 120, 200), hover=(90, 160, 240)):
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
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, r, 2)


def _grid():

    screen.fill(BG_COLOR)
    for i in range(0, SCREEN_W, 40):
        pygame.draw.line(screen, (25, 25, 50), (i, 0), (i, SCREEN_H))
    for i in range(0, SCREEN_H, 40):
        pygame.draw.line(screen, (25, 25, 50), (0, i), (SCREEN_W, i))


def menu_Spielerzahl():
    title = font_big.render("Normal", True, (255, 255, 255))
    subtitle = font_small.render("Was willst du spielen", True,
                                 (200, 200, 200))
    menu_G = True


    btn_N = Button((SCREEN_W // 2 - 200, 350, 400, 90), "Normal")
    btn_1vs2 = Button((SCREEN_W // 2 - 200, 450, 400, 90), "1 vs.2")
    btn_2 = Button((SCREEN_W // 2 - 200, 550, 400, 90), "2")
    btn_s_1 = Button((SCREEN_W // 2 - 200, 350, 400, 90), "1 Spieler")
    btn_s_2 = Button((SCREEN_W // 2 - 200, 450, 400, 90), "2 Spieler")
    btn_s_3 = Button((SCREEN_W // 2 - 200, 550, 400, 90), "3 Spieler")
    btn_quit_s = Button((SCREEN_W // 2 - 200, 710, 400, 90), "Beenden",
                      color=(150, 50, 50), hover=(200, 70, 70))

    while menu_G:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn_N.clicked(p):
                    Gamemode = "Normal"
                    menu_G = False
                    Spielerzahl_menu = True
                if btn_1vs2.clicked(p):
                    Gamemode = "1 vs. 2"
                    return 3, Gamemode
                if btn_2.clicked(p):
                    Gamemode = "2"
                    menu_G = False
                    Spielerzahl_menu = True
                if btn_quit_s.clicked(p):
                    return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    Gamemode = "Normal"
                    menu_G = False
                    Spielerzahl_menu = True
                if event.key == pygame.K_2:
                    Gamemode = "Extra"
                    menu_G = False
                    Spielerzahl_menu = True
                if event.key == pygame.K_3:
                    Gamemode = "2"
                    Spielerzahl_menu = True
                if event.key == pygame.K_ESCAPE:
                    return None


        _grid()
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 320)))
        btn_N.draw(screen, mouse_pos)
        btn_1vs2.draw(screen, mouse_pos)
        btn_2.draw(screen, mouse_pos)
        btn_quit_s.draw(screen, mouse_pos)

        CTX.present()
        clock.tick(60)

    screen.fill(BG_COLOR)

    while Spielerzahl_menu == True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn_s_1.clicked(p):
                    return 1, Gamemode
                if btn_s_2.clicked(p):
                    return 2, Gamemode
                if btn_s_3.clicked(p):
                    return 3, Gamemode
                if btn_quit_s.clicked(p):
                    choice, Gamemode = menu_Spielerzahl()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1, Gamemode
                if event.key == pygame.K_2:
                    return 2, Gamemode
                if event.key == pygame.K_3:
                    return 3, Gamemode
                if event.key == pygame.K_ESCAPE:
                    choice, Gamemode = menu_Spielerzahl()
        info = [
            "Spieler 1 (blau):  Pfeiltasten",
            "Spieler 2 (grün):  W A S D",
            "Spieler 3 (gelb):  I J K L",
            "Wenn zwei Schlangen kollidieren, stirbt die mit dem kleineren Level.",
            "Der Sieger wächst um 50%. Letzte Schlange gewinnt!",
        ]
        _grid()
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 320)))
        btn_s_1.draw(screen, mouse_pos)
        btn_s_2.draw(screen, mouse_pos)
        btn_s_3.draw(screen, mouse_pos)
        btn_quit_s.draw(screen, mouse_pos)
        for i, line in enumerate(info):
            t = font_small.render(line, True, (180, 180, 200))
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 850 + i * 30)))
        CTX.present()
        clock.tick(60)


def winner_screen(winner_name, winner_color, snakes, Gamemode):
    btn_again = Button((SCREEN_W // 2 - 200, 600, 400, 90), "Nochmal")
    btn_menu = Button((SCREEN_W // 2 - 200, 700, 400, 90), "Zurück zum Menü")
    while True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.clicked(CTX.map(event.pos)):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_again.clicked(CTX.map(event.pos)):



                    if len(snakes) == 2:
                        return play_game(num_players=2, Gamemode = "Normal")
                    if len(snakes) == 3:
                        return play_game(num_players=3, Gamemode = "Normal")



            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:

                    if Gamemode == "Normal":
                        if len(snakes) == 2:
                            return play_game(num_players=2, Gamemode="Normal")
                        if len(snakes) == 3:
                            return play_game(num_players=3, Gamemode="Normal")
                    if Gamemode == "1 vs. 2":
                        if len(snakes) == 2:
                            return play_game(num_players=2, Gamemode="1 vs. 2")
                        if len(snakes) == 3:
                            return play_game(num_players=3, Gamemode="1 vs. 2")
                    else:
                        if len(snakes) == 2:
                            return play_game(num_players=2, Gamemode="Normal")
                        if len(snakes) == 3:
                            return play_game(num_players=3, Gamemode="Normal")
        _grid()
        title = font_big.render("🏆 Gewinner!", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 300)))
        name_surf = font_big.render(f"{winner_name}", True, winner_color)
        screen.blit(name_surf, name_surf.get_rect(center=(SCREEN_W // 2, 450)))
        sub = font_mid.render("hat das Spiel gewonnen!", True, (220, 220, 220))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 560)))
        btn_again.draw(screen, mouse_pos)
        btn_menu.draw(screen, mouse_pos)
        CTX.present()
        clock.tick(60)

def play_game(num_players, Gamemode):  # self entfernt, da es eine normale Funktion ist
        if Gamemode == "Normal":
            eyes_color_1 = (255, 255, 255)
            eyes_color_2 = (255, 255, 255)
            eyes_color_3 = (255, 255, 255)
            Normal_color_1 = (255, 55, 0)
            Normal_color_2 = (55, 0, 255)
            Normal_color_3 = (0, 255, 55)
            print(Gamemode)
        elif Gamemode == "1 vs. 2":
            eyes_color_1 = (255, 255, 255)
            eyes_color_2 = (255, 0, 0)
            eyes_color_3 = (0, 255, 0)
            Normal_color_1 = (255, 0, 0)
            Normal_color_2 = (0, 0, 255)
            Normal_color_3 = (0, 0, 255)
            print(Gamemode)
        else:
            eyes_color_1 = (255, 255, 255)
            eyes_color_2 = (255, 255, 255)
            eyes_color_3 = (255, 255, 255)
            Normal_color_1 = (255, 55, 0)
            Normal_color_2 = (55, 0, 255)
            Normal_color_3 = (0, 55, 255)
            print(Gamemode)

        snakes = []
        if num_players >= 1:
            snakes.append(Snake(
                "Spieler 1", (SCREEN_W - 100, SCREEN_H - 100), Normal_color_1, eyes_color_1,
                {"up": pygame.K_UP, "down": pygame.K_DOWN,
                 "left": pygame.K_LEFT, "right": pygame.K_RIGHT}))
        if num_players >= 2:
            snakes.append(Snake(
                "Spieler 2", (50, 50), Normal_color_2, eyes_color_2,
                {"up": pygame.K_w, "down": pygame.K_s,
                 "left": pygame.K_a, "right": pygame.K_d}))
        if num_players >= 3:
            snakes.append(Snake(
                "Spieler 3", (SCREEN_W // 2, SCREEN_H // 2), Normal_color_3, eyes_color_3,
                {"up": pygame.K_i, "down": pygame.K_k,
                 "left": pygame.K_j, "right": pygame.K_l}))

        wechsler = Wechsler()
        winner = None
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return True

            keys = pygame.key.get_pressed()
            for s in snakes:
                s.handle_input(keys)
                s.update_trail()

            wechsler.update()
            if wechsler.active:
                for s in snakes:
                    if s.alive and not s.dying and s.rect.colliderect(wechsler.rect):
                        if random.randint(1, 2) == 1:
                            s.speed += 1
                            s.max_trail = s.speed * 2
                            new_speed = s.speed
                        else:
                            s.grow(1.2)




                        s.level += 1

                        wechsler.consume()
                        break

            alive_snakes = [s for s in snakes if s.alive and not s.dying]
            for i in range(len(alive_snakes)):
                for j in range(i + 1, len(alive_snakes)):
                    a = alive_snakes[i]
                    b = alive_snakes[j]

                    if a.collides_with(b):
                        # Team-Check für Modus "1 vs. 2": Spieler 2 und Spieler 3 tun sich nichts
                        if Gamemode == "1 vs. 2":
                            if (a.name == "Spieler 2" and b.name == "Spieler 3") or \
                                    (a.name == "Spieler 3" and b.name == "Spieler 2"):
                                continue  # Überspringt die Kollision, kein Schaden untereinander

                        # Wer gewinnt den Kampf?
                        if a.level > b.level:
                            loser, winner_snake = b, a
                        elif a.level < b.level:
                            loser, winner_snake = a, b
                        else:
                            # Bei Gleichstand sterben entweder beide, oder es passiert nichts.
                            # Hier gelöst: Beide prallen ab (keiner stirbt), um Softlocks zu verhindern.
                            continue

                        loser.start_death()
                        winner_snake.grow(3.5)  # 2.5 war extrem riesig, 1.5 passt besser zum Screen
                        print(f"{winner_snake.name} hat {loser.name} besiegt!")

            for s in snakes:
                if s.dying:
                    s.death_timer += 1
                    if s.death_timer >= s.death_max:
                        s.dying = False
                        s.alive = False

            living = [s for s in snakes if s.alive]
            dying_now = [s for s in snakes if s.dying]

            # Spielende-Bedingung
            if num_players != 1:
                if len(living) <= 1 and not dying_now:
                    winner = living[0] if living else None
                    running = False
            if Gamemode == "1 vs. 2":
                if len(dying_now) != 0:
                    if dying_now[0].name == "Spieler 1":
                        winner_team = "Team Blau"
                        return winner_screen(winner_team, Normal_color_2, snakes)
            else:
                # Für Einzelspieler: Spiel läuft einfach weiter, bis man ESC drückt
                if len(living) == 0 and not dying_now:
                    running = False

            _grid()
            wechsler.draw(screen)
            for s in snakes:
                s.draw(screen)

            for idx, s in enumerate(snakes):
                status = "TOT" if not s.alive and not s.dying else f"Größe {s.size}"
                txt = font_small.render(f"{s.name}: {status}  Level: {s.level}", True, s.base_color)
                screen.blit(txt, (20, 20 + idx * 32))

            CTX.present()
            clock.tick(60)

        if winner:
            return winner_screen(winner.name, winner.base_color, snakes, Gamemode)
        return winner_screen("Niemand", (200, 200, 200), snakes, Gamemode)

def main(ctx):
    global screen, clock, font_big, font_mid, font_small, CTX
    CTX = ctx
    screen = ctx.surf
    clock = ctx.clock
    font_big = ctx.font_big
    font_mid = ctx.font_mid
    font_small = ctx.font_small
    while True:
        choice, Gamemode = menu_Spielerzahl()
        if choice is None:
            return Gamemode


        if not play_game(choice, Gamemode):
            return Gamemode


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




