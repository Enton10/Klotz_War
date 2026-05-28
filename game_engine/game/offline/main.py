import random, math, pygame

SCREEN_W, SCREEN_H = 1900, 1000
BG_COLOR = (15, 15, 30)

screen = clock = font_big = font_mid = font_small = CTX = None


class Snake:
    def __init__(self, name, start_pos, color, controls, size=20):
        self.name = name
        self.color = color
        self.base_color = color
        self.size = size
        self.controls = controls
        self.rect = pygame.Rect(start_pos[0], start_pos[1], size, size)
        self.speed = 5
        self.trail = []
        self.max_trail = 18
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
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
            ex = self.rect.x + self.size // 4
            ey = self.rect.y + self.size // 4
            pygame.draw.circle(surface, (255, 255, 255),
                               (ex, ey), max(2, self.size // 8))
            pygame.draw.circle(surface, (255, 255, 255),
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


def menu():
    title = font_big.render("Willkommen", True, (255, 255, 255))
    subtitle = font_small.render("Wähle die Anzahl der Spieler", True,
                                 (200, 200, 200))
    btn2 = Button((SCREEN_W // 2 - 200, 450, 400, 90), "2 Spieler")
    btn3 = Button((SCREEN_W // 2 - 200, 580, 400, 90), "3 Spieler")
    btn_quit = Button((SCREEN_W // 2 - 200, 710, 400, 90), "Beenden",
                      color=(150, 50, 50), hover=(200, 70, 70))
    info = [
        "Spieler 1 (blau):  Pfeiltasten",
        "Spieler 2 (grün):  W A S D",
        "Spieler 3 (gelb):  I J K L",
        "Wenn zwei Schlangen kollidieren, stirbt zufällig eine.",
        "Der Sieger wächst um 50%. Letzte Schlange gewinnt!",
    ]
    while True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                p = CTX.map(event.pos)
                if btn2.clicked(p):
                    return 2
                if btn3.clicked(p):
                    return 3
                if btn_quit.clicked(p):
                    return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    return 2
                if event.key == pygame.K_3:
                    return 3
                if event.key == pygame.K_ESCAPE:
                    return None

        _grid()
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 200)))
        screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 320)))
        btn2.draw(screen, mouse_pos)
        btn3.draw(screen, mouse_pos)
        btn_quit.draw(screen, mouse_pos)
        for i, line in enumerate(info):
            t = font_small.render(line, True, (180, 180, 200))
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 850 + i * 30)))
        CTX.present()
        clock.tick(60)


def winner_screen(winner_name, winner_color):
    btn_menu = Button((SCREEN_W // 2 - 200, 700, 400, 90), "Zurück zum Menü")
    while True:
        mouse_pos = CTX.mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.clicked(CTX.map(event.pos)):
                    return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    return True
        _grid()
        title = font_big.render("🏆 Gewinner!", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 300)))
        name_surf = font_big.render(f"{winner_name}", True, winner_color)
        screen.blit(name_surf, name_surf.get_rect(center=(SCREEN_W // 2, 450)))
        sub = font_mid.render("hat das Spiel gewonnen!", True, (220, 220, 220))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 560)))
        btn_menu.draw(screen, mouse_pos)
        CTX.present()
        clock.tick(60)


def play_game(num_players):
    snakes = []
    snakes.append(Snake(
        "Spieler 1 (Blau)", (SCREEN_W - 100, SCREEN_H - 100), (60, 120, 255),
        {"up": pygame.K_UP, "down": pygame.K_DOWN,
         "left": pygame.K_LEFT, "right": pygame.K_RIGHT}))
    snakes.append(Snake(
        "Spieler 2 (Grün)", (50, 50), (60, 220, 90),
        {"up": pygame.K_w, "down": pygame.K_s,
         "left": pygame.K_a, "right": pygame.K_d}))
    if num_players >= 3:
        snakes.append(Snake(
            "Spieler 3 (Gelb)", (SCREEN_W // 2, SCREEN_H // 2), (240, 220, 60),
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
                if s.alive and not s.dying and \
                        s.rect.colliderect(wechsler.rect):
                    if random.randint(1, 2) == 1:
                        s.speed += 1
                    else:
                        s.grow(1.2)
                    wechsler.consume()
                    break

        alive_snakes = [s for s in snakes if s.alive and not s.dying]
        for i in range(len(alive_snakes)):
            for j in range(i + 1, len(alive_snakes)):
                a = alive_snakes[i]
                b = alive_snakes[j]
                if a.collides_with(b):
                    total = a.size + b.size
                    if random.random() < a.size / total:
                        loser, winner_snake = b, a
                    else:
                        loser, winner_snake = a, b
                    loser.start_death()
                    winner_snake.grow(1.5)
                    print(f"{winner_snake.name} hat {loser.name} besiegt!")

        for s in snakes:
            if s.dying:
                s.death_timer += 1
                if s.death_timer >= s.death_max:
                    s.dying = False
                    s.alive = False

        living = [s for s in snakes if s.alive]
        dying_now = [s for s in snakes if s.dying]
        if len(living) <= 1 and not dying_now:
            winner = living[0] if living else None
            running = False

        _grid()
        wechsler.draw(screen)
        for s in snakes:
            s.draw(screen)
        for idx, s in enumerate(snakes):
            status = "TOT" if not s.alive and not s.dying \
                else f"Größe {s.size}"
            txt = font_small.render(f"{s.name}: {status}", True, s.base_color)
            screen.blit(txt, (20, 20 + idx * 32))

        CTX.present()
        clock.tick(60)

    if winner:
        return winner_screen(winner.name, winner.base_color)
    return winner_screen("Niemand", (200, 200, 200))


def main(ctx):
    global screen, clock, font_big, font_mid, font_small, CTX
    CTX = ctx
    screen = ctx.surf
    clock = ctx.clock
    font_big = ctx.font_big
    font_mid = ctx.font_mid
    font_small = ctx.font_small
    while True:
        choice = menu()
        if choice is None:
            break
        if not play_game(choice):
            break


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
