import socket, json, math, hashlib, threading, random, pygame

SCREEN_W, SCREEN_H = 1900, 1000
BG_COLOR = (15, 15, 30)
GRID = (25, 25, 50)

screen = clock = font_big = font_mid = font_small = CTX = None


class Button:
    def __init__(self, rect, text, color=(60, 120, 200), hover=(90, 160, 240)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = hover

    def draw(self, mouse_pos):
        c = self.hover if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=14)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3,
                         border_radius=14)
        label = font_mid.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Net:
    def __init__(self, sock):
        self.sock = sock
        self.buf = b""
        self.lock = threading.Lock()
        self.world = None
        self.events = []
        self.ok = True

    def readline(self):
        while b"\n" not in self.buf:
            d = self.sock.recv(4096)
            if not d:
                raise ConnectionError
            self.buf += d
        line, self.buf = self.buf.split(b"\n", 1)
        return line

    def send(self, obj):
        try:
            self.sock.sendall((json.dumps(obj) + "\n").encode())
        except Exception:
            self.ok = False

    def run(self):
        try:
            while True:
                line = self.readline()
                if not line.strip():
                    continue
                m = json.loads(line)
                with self.lock:
                    if m["t"] == "world":
                        self.world = m
                    elif m["t"] == "event":
                        self.events.append(m)
        except Exception:
            self.ok = False

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def _grid():
    screen.fill(BG_COLOR)
    for x in range(0, SCREEN_W, 40):
        pygame.draw.line(screen, GRID, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, 40):
        pygame.draw.line(screen, GRID, (0, y), (SCREEN_W, y))


def _recvn(sock, n):
    b = b""
    while len(b) < n:
        d = sock.recv(n - len(b))
        if not d:
            raise ConnectionError
        b += d
    return b


def _msg_screen(text, color=(255, 80, 80)):
    t = pygame.time.get_ticks()
    while pygame.time.get_ticks() - t < 1800:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                return True
        _grid()
        s = font_mid.render(text, True, color)
        screen.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        CTX.present()
        clock.tick(30)
    return True


def _draw_snake(x, y, size, color, dying, dt, trail):
    for i, (tx, ty, ts) in enumerate(trail):
        alpha = int(80 + (i / max(1, len(trail))) * 150)
        s = pygame.Surface((ts, ts), pygame.SRCALPHA)
        s.fill((min(color[0], 255), min(color[1], 255),
                min(color[2], 255), alpha))
        screen.blit(s, (tx, ty))
    if dying:
        cx, cy = int(x + size / 2), int(y + size / 2)
        radius = int(size * (1 + dt * 4)) + 1
        alpha = max(0, int(255 * (1 - dt)))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 50, 50, alpha), (radius, radius), radius)
        screen.blit(s, (cx - radius, cy - radius))
        for _ in range(3):
            px = cx + random.randint(-radius, radius)
            py = cy + random.randint(-radius, radius)
            pygame.draw.circle(screen, (255, 200, 0), (px, py),
                               random.randint(2, 5))
    else:
        r = pygame.Rect(int(x), int(y), size, size)
        pygame.draw.rect(screen, color, r, border_radius=6)
        ex = r.x + size // 4
        ey = r.y + size // 4
        pygame.draw.circle(screen, (255, 255, 255), (ex, ey),
                           max(2, size // 8))
        pygame.draw.circle(screen, (255, 255, 255),
                           (ex + size // 2, ey), max(2, size // 8))


def _winner_screen(winner):
    btn = Button((SCREEN_W // 2 - 200, 700, 400, 90), "Zurück zum Menü")
    if winner is None:
        name, color = "Niemand", (200, 200, 200)
    else:
        name, color = winner["name"], tuple(winner["color"])
    while True:
        mp = CTX.mouse()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.MOUSEBUTTONDOWN and btn.clicked(
                    CTX.map(ev.pos)):
                return True
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return False
                if ev.key == pygame.K_RETURN:
                    return True
        _grid()
        title = font_big.render("🏆 Gewinner!", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 300)))
        ns = font_big.render(name, True, color)
        screen.blit(ns, ns.get_rect(center=(SCREEN_W // 2, 450)))
        sub = font_mid.render("hat das Spiel gewonnen!", True, (220, 220, 220))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 560)))
        btn.draw(mp)
        CTX.present()
        clock.tick(60)


def _wait_overlay(count):
    msg = font_mid.render("Warte auf Mitspieler ...", True, (255, 255, 255))
    screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
    sub = font_small.render(f"Verbundene Spieler: {count}", True,
                            (180, 180, 200))
    screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))


def main(ctx, host, port, token, pw=""):
    global screen, clock, font_big, font_mid, font_small, CTX
    CTX = ctx
    screen = ctx.surf
    clock = ctx.clock
    font_big = ctx.font_big
    font_mid = ctx.font_mid
    font_small = ctx.font_small

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect((host, int(port)))
        sock.sendall(hashlib.sha256((token + ":" + pw).encode())
                     .hexdigest().encode())
        ack = _recvn(sock, 64).decode().strip()
        if ack != hashlib.sha256((token + ":" + pw + ":ACK").encode()) \
                .hexdigest():
            return _msg_screen("Authentifizierung fehlgeschlagen")
        sock.settimeout(None)
    except Exception:
        return _msg_screen("Verbindung fehlgeschlagen")

    net = Net(sock)
    net.send({"t": "hello", "name": "Spieler"})
    try:
        wel = json.loads(net.readline())
    except Exception:
        net.close()
        return _msg_screen("Keine Server-Antwort")

    pid = wel["id"]
    px, py = wel["start"]
    W = wel.get("w", SCREEN_W)
    H = wel.get("h", SCREEN_H)
    size = 20
    speed = 5

    threading.Thread(target=net.run, daemon=True).start()

    trails = {}
    running = True
    final_winner = None
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                net.close()
                return False
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                net.close()
                return True

        with net.lock:
            world = net.world
            evs = net.events
            net.events = []

        for e in evs:
            k = e.get("kind")
            if k == "speed":
                speed += 1
            elif k == "respawn":
                px, py = e["x"], e["y"]
                speed = 5

        me = None
        if world:
            for p in world["players"]:
                if p["id"] == pid:
                    me = p
                    break
        if me:
            size = me["size"]

        alive = (me is None) or (me["alive"] and not me["dying"])
        playing = world is not None and world.get("phase") == "play"

        keys = pygame.key.get_pressed()
        if alive and playing:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                px -= speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                px += speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                py -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                py += speed
            px = max(0, min(W - size, px))
            py = max(0, min(H - size, py))

        net.send({"t": "state", "x": int(px), "y": int(py)})

        if not net.ok:
            net.close()
            return _msg_screen("Verbindung verloren")

        if world and world.get("phase") == "over":
            final_winner = world.get("winner")
            running = False

        _grid()

        wech = world.get("wech") if world else None
        if wech and wech["active"]:
            r = 12 + int(4 * math.sin(pygame.time.get_ticks() / 150))
            pygame.draw.circle(screen, (0, 230, 230),
                               (wech["x"], wech["y"]), r)
            pygame.draw.circle(screen, (255, 255, 255),
                               (wech["x"], wech["y"]), r, 2)

        live_ids = set()
        if world:
            for p in world["players"]:
                live_ids.add(p["id"])
                x, y = (px, py) if p["id"] == pid else (p["x"], p["y"])
                color = tuple(p["color"])
                tr = trails.setdefault(p["id"], [])
                if p["alive"] and not p["dying"]:
                    tr.append((int(x), int(y), p["size"]))
                    if len(tr) > 18:
                        tr.pop(0)
                if p["alive"] or p["dying"]:
                    _draw_snake(x, y, p["size"], color, p["dying"],
                                p["dt"], tr)
        for k in list(trails.keys()):
            if k not in live_ids:
                trails.pop(k, None)

        if world:
            for idx, p in enumerate(world["players"]):
                if not p["alive"] and not p["dying"]:
                    st = "TOT"
                else:
                    st = f"Größe {p['size']}"
                tag = " (du)" if p["id"] == pid else ""
                txt = font_small.render(f"{p['name']}{tag}: {st}", True,
                                        tuple(p["color"]))
                screen.blit(txt, (20, 20 + idx * 32))

        if world and world.get("phase") == "wait":
            _wait_overlay(len(world["players"]))

        CTX.present()
        clock.tick(60)

    net.close()
    return _winner_screen(final_winner)


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
    import sys
    h = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 7331
    pwd = sys.argv[3] if len(sys.argv) > 3 else ""
    main(_DevCtx(), h, p, "l1rox3:7Nk2QvPx9mZgE4wR:hx91", pwd)
