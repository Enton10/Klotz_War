import sys, os, json, socket, hashlib, importlib.util, threading, pygame, time
from pathlib import Path

_TK = "l1rox3:7Nk2QvPx9mZgE4wR:hx91"
_BASE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_BASE)
_OFF = os.path.join(_BASE, "offline", "main.py")
_ONL = os.path.join(_BASE, "online", "main.py")
_SRV = os.path.join(_ROOT, "server", "main.py")
_DEF_HOST = "127.0.0.1"
_DEF_PORT = 7331
_DISC_PORT = 7332
_DT = Path("warn.txt")
_SO = Path(__file__).parent
_SW, _SH = 1900, 1000
_BG = (15, 15, 30)
_GR = (25, 25, 50)

_ctx = _sf = _clk = _fb = _fm = _fs = None
_gs = None


class Ctx:
    def __init__(self, win, surf, clock, fb, fm, fs, w, h, scale):
        self.win = win
        self.surf = surf
        self.clock = clock
        self.font_big = fb
        self.font_mid = fm
        self.font_small = fs
        self.W = w
        self.H = h
        self.scale = scale

    def present(self):
        self.win.blit(self.surf, (0, 0))
        pygame.display.flip()

    def map(self, pos):
        return pos

    def mouse(self):
        return pygame.mouse.get_pos()


class Discovery:
    def __init__(self):
        self.servers = {}
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            pass
        self.sock.bind(("", _DISC_PORT))
        self.sock.settimeout(0.3)
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                m = json.loads(data.decode())
                if m.get("magic") == "KLOTZ1":
                    key = (addr[0], int(m["port"]))
                    self.servers[key] = {"name": m.get("name", "?"),
                                         "pw": bool(m.get("pw")),
                                         "players": int(m.get("players", 0)),
                                         "seen": pygame.time.get_ticks()}
            except socket.timeout:
                pass
            except Exception:
                pass
            self._expire()

    def _expire(self):
        now = pygame.time.get_ticks()
        for k in list(self.servers):
            if now - self.servers[k]["seen"] > 4000:
                self.servers.pop(k, None)

    def list(self):
        return [(ip, port, info)
                for (ip, port), info in sorted(self.servers.items())]

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass


def _pf():
    if sys.version_info < (3, 9):
        print("Python 3.9+ required")
        sys.exit(2)
    try:
        pygame.init()
    except Exception:
        print("Pygame initialization failed")
        sys.exit(3)
    if not os.path.isfile(_OFF):
        print(f"Missing file: {_OFF}")
        sys.exit(4)


def _ui():
    global _ctx, _sf, _clk, _fb, _fm, _fs
    win = pygame.display.set_mode((_SW, _SH), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("game engine")
    _sf = pygame.Surface((_SW, _SH))
    _clk = pygame.time.Clock()
    _fb = pygame.font.SysFont("arial", 72, bold=True)
    _fm = pygame.font.SysFont("arial", 42, bold=True)
    _fs = pygame.font.SysFont("arial", 28)
    _ctx = Ctx(win, _sf, _clk, _fb, _fm, _fs, _SW, _SH, 1.0)

def _bg():
    _sf.fill(_BG)
    for x in range(0, _SW, 40):
        pygame.draw.line(_sf, _GR, (x, 0), (x, _SH))
    for y in range(0, _SH, 40):
        pygame.draw.line(_sf, _GR, (0, y), (_SW, y))


def _dbtn(rect, lbl, mp, c=(60, 120, 200), hc=(90, 160, 240)):
    r = pygame.Rect(rect)
    pygame.draw.rect(_sf, hc if r.collidepoint(mp) else c, r, border_radius=14)
    pygame.draw.rect(_sf, (255, 255, 255), r, 3, border_radius=14)
    t = _fm.render(lbl, True, (255, 255, 255))
    _sf.blit(t, t.get_rect(center=r.center))
    return r


def _dibox(rect, val, active):
    r = pygame.Rect(rect)
    pygame.draw.rect(_sf, (20, 20, 40), r, border_radius=8)
    pygame.draw.rect(_sf, (80, 160, 255) if active else (50, 50, 80), r, 2,
                     border_radius=8)
    if val:
        t = _fs.render(val, True, (220, 220, 220))
        _sf.blit(t, (r.x + 12, r.centery - t.get_height() // 2))
    return r


def _load(path, tag):
    sp = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _hs(host, port, pw):
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(6)
        sk.connect((host, port))
        sk.sendall(hashlib.sha256((_TK + ":" + pw).encode())
                   .hexdigest().encode())
        r = sk.recv(64).decode().strip()
        sk.close()
        return r == hashlib.sha256((_TK + ":" + pw + ":ACK").encode()) \
            .hexdigest()
    except Exception:
        return False


def _mode_sel():
    r_off = r_loc = r_pub = r_q = pygame.Rect(0, 0, 0, 0)
    while True:
        mp = _ctx.mouse()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                print("Exiting launcher.")
                return None
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                print("Exiting launcher.")
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN:
                p = _ctx.map(ev.pos)
                if r_off.collidepoint(p):
                    print("Selected mode: offline")
                    return "offline"
                if r_loc.collidepoint(p):
                    print("Selected mode: local")
                    return "local"
                if r_pub.collidepoint(p):
                    print("Selected mode: public")
                    return "public"
                if r_q.collidepoint(p):
                    print("Exiting launcher.")
                    return None

        _bg()
        h = _fb.render("Hey! Pick your mode.", True, (255, 255, 255))
        _sf.blit(h, h.get_rect(center=(_SW // 2, 190)))

        r_off = _dbtn((_SW // 2 - 200, 370, 400, 90), "Offline", mp)
        r_loc = _dbtn((_SW // 2 - 200, 490, 400, 90), "Local", mp)
        r_pub = _dbtn((_SW // 2 - 200, 610, 400, 90), "Online", mp)
        r_q = _dbtn((_SW // 2 - 200, 770, 400, 90), "Quit", mp,
                    (150, 50, 50), (200, 70, 70))

        _ctx.present()
        _clk.tick(60)


def _srv_input(local=False):
    host = "192.168.1." if local else _DEF_HOST
    port = str(_DEF_PORT)
    pw = ""
    foc = "h"
    msg = ""
    rh = rp = rw = rb = rx = pygame.Rect(0, 0, 0, 0)

    while True:
        mp = _ctx.mouse()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None, None, None
            if ev.type == pygame.MOUSEBUTTONDOWN:
                p = _ctx.map(ev.pos)
                if rh.collidepoint(p):
                    foc = "h"
                elif rp.collidepoint(p):
                    foc = "p"
                elif rw.collidepoint(p):
                    foc = "w"
                if rb.collidepoint(p):
                    try:
                        if host.strip():
                            return host.strip(), int(port), pw
                    except ValueError:
                        msg = "Ungültiger Port"
                if rx.collidepoint(p):
                    return None, None, None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None, None, None
                if ev.key == pygame.K_TAB:
                    foc = {"h": "p", "p": "w", "w": "h"}[foc]
                if ev.key == pygame.K_RETURN:
                    try:
                        if host.strip():
                            return host.strip(), int(port), pw
                    except ValueError:
                        msg = "Ungültiger Port"
                if foc == "h":
                    if ev.key == pygame.K_BACKSPACE:
                        host = host[:-1]
                    elif len(host) < 64:
                        host += ev.unicode
                elif foc == "p":
                    if ev.key == pygame.K_BACKSPACE:
                        port = port[:-1]
                    elif len(port) < 6 and ev.unicode.isdigit():
                        port += ev.unicode
                else:
                    if ev.key == pygame.K_BACKSPACE:
                        pw = pw[:-1]
                    elif len(pw) < 32 and ev.unicode.isprintable():
                        pw += ev.unicode

        _bg()
        t = _fm.render("Lokaler Server" if local else "Server", True,
                       (255, 255, 255))
        _sf.blit(t, t.get_rect(center=(_SW // 2, 170)))

        _sf.blit(_fs.render("Host / IP", True, (180, 180, 200)),
                 (_SW // 2 - 300, 290))
        rh = _dibox((_SW // 2 - 300, 320, 600, 52), host, foc == "h")

        _sf.blit(_fs.render("Port", True, (180, 180, 200)),
                 (_SW // 2 - 300, 405))
        rp = _dibox((_SW // 2 - 300, 435, 200, 52), port, foc == "p")

        _sf.blit(_fs.render("Passwort", True, (180, 180, 200)),
                 (_SW // 2 - 300, 520))
        rw = _dibox((_SW // 2 - 300, 550, 600, 52), "*" * len(pw), foc == "w")

        if msg:
            em = _fs.render(msg, True, (255, 80, 80))
            _sf.blit(em, em.get_rect(center=(_SW // 2, 640)))

        rb = _dbtn((_SW // 2 - 200, 680, 400, 80), "Verbinden", mp)
        rx = _dbtn((_SW // 2 - 200, 790, 400, 80), "Zurück", mp,
                   (100, 100, 100), (140, 140, 140))

        _ctx.present()
        _clk.tick(60)


def _local_menu():
    disc = Discovery()
    pw = ""
    af_pw = False
    rows = []
    r_host = r_man = r_back = r_pwbox = pygame.Rect(0, 0, 0, 0)
    try:
        while True:
            mp = _ctx.mouse()
            servers = disc.list()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return None
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    p = _ctx.map(ev.pos)
                    af_pw = r_pwbox.collidepoint(p)
                    if r_host.collidepoint(p):
                        return ("host",)
                    if r_man.collidepoint(p):
                        return ("manual",)
                    if r_back.collidepoint(p):
                        return None
                    for rect, ip, port in rows:
                        if rect.collidepoint(p):
                            print(f"Joining {ip}:{port}")
                            return ("join", ip, port, pw)
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        return None
                    if af_pw:
                        if ev.key == pygame.K_BACKSPACE:
                            pw = pw[:-1]
                        elif len(pw) < 32 and ev.unicode.isprintable():
                            pw += ev.unicode

            _bg()
            t = _fb.render("Lokales Netzwerk", True, (255, 255, 255))
            _sf.blit(t, t.get_rect(center=(_SW // 2, 110)))

            r_host = _dbtn((_SW // 2 - 200, 200, 400, 80), "Server hosten",
                           mp, (60, 180, 110), (80, 210, 130))

            _sf.blit(_fs.render("Gefundene Server:", True, (180, 180, 200)),
                     (_SW // 2 - 450, 320))
            rows = []
            y = 360
            if not servers:
                hint = _fs.render("Suche im Netzwerk ...", True,
                                  (120, 120, 150))
                _sf.blit(hint, (_SW // 2 - 450, y + 10))
            for ip, port, info in servers[:6]:
                rect = pygame.Rect(_SW // 2 - 450, y, 900, 56)
                bgc = (40, 40, 70) if rect.collidepoint(mp) else (24, 24, 46)
                pygame.draw.rect(_sf, bgc, rect, border_radius=10)
                pygame.draw.rect(_sf, (80, 160, 255), rect, 2,
                                 border_radius=10)
                lock = "Passwort" if info["pw"] else "offen"
                label = (f"{info['name']}    {ip}:{port}    {lock}"
                         f"    Spieler: {info['players']}")
                _sf.blit(_fs.render(label, True, (220, 220, 220)),
                         (rect.x + 16, rect.centery - 14))
                rows.append((rect, ip, port))
                y += 66

            _sf.blit(_fs.render("Passwort (zum Beitreten):", True,
                                (180, 180, 200)), (_SW // 2 - 450, 800))
            r_pwbox = _dibox((_SW // 2 - 450, 832, 400, 48),
                             "*" * len(pw), af_pw)
            r_man = _dbtn((_SW // 2 + 60, 824, 390, 64), "Manuell", mp,
                          (100, 100, 100), (140, 140, 140))
            r_back = _dbtn((_SW // 2 - 200, 912, 400, 64), "Zurück", mp,
                           (120, 60, 60), (160, 80, 80))

            _ctx.present()
            _clk.tick(60)
    finally:
        disc.stop()


def _host_config():
    name = "Mein Server"
    pw = ""
    af_n, af_p = True, False
    r_n = r_p = r_s = r_b = pygame.Rect(0, 0, 0, 0)
    while True:
        mp = _ctx.mouse()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return None
            if ev.type == pygame.MOUSEBUTTONDOWN:
                p = _ctx.map(ev.pos)
                af_n = r_n.collidepoint(p)
                af_p = r_p.collidepoint(p)
                if r_s.collidepoint(p) and name.strip():
                    return name.strip(), pw
                if r_b.collidepoint(p):
                    return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return None
                if ev.key == pygame.K_TAB:
                    af_n, af_p = not af_n, not af_p
                if ev.key == pygame.K_RETURN and name.strip():
                    return name.strip(), pw
                if af_n:
                    if ev.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 16 and ev.unicode.isprintable():
                        name += ev.unicode
                elif af_p:
                    if ev.key == pygame.K_BACKSPACE:
                        pw = pw[:-1]
                    elif len(pw) < 32 and ev.unicode.isprintable():
                        pw += ev.unicode

        _bg()
        t = _fm.render("Server hosten", True, (255, 255, 255))
        _sf.blit(t, t.get_rect(center=(_SW // 2, 200)))

        _sf.blit(_fs.render("Servername", True, (180, 180, 200)),
                 (_SW // 2 - 300, 330))
        r_n = _dibox((_SW // 2 - 300, 360, 600, 52), name, af_n)

        _sf.blit(_fs.render("Passwort (leer = keins)", True, (180, 180, 200)),
                 (_SW // 2 - 300, 445))
        r_p = _dibox((_SW // 2 - 300, 475, 600, 52), "*" * len(pw), af_p)

        r_s = _dbtn((_SW // 2 - 200, 600, 400, 80), "Starten", mp,
                    (60, 180, 110), (80, 210, 130))
        r_b = _dbtn((_SW // 2 - 200, 710, 400, 80), "Zurück", mp,
                    (100, 100, 100), (140, 140, 140))

        _ctx.present()
        _clk.tick(60)


def _host_start(name, pw, port):
    global _gs
    if _gs is not None:
        _gs.stop()
        _gs = None
    try:
        srvmod = _load(_SRV, "klotz_server")
        gs = srvmod.GS(name, pw, "0.0.0.0", port)
        gs.run_bg()
        _gs = gs
        print(f"Hosting '{name}' on port {port}")
        return gs
    except Exception as e:
        print(f"Host start failed: {e}")
        return None


def _conn_screen(host, port, pw):
    pygame.event.clear()
    result = [None]
    print(f"Attempting connection to {host}:{port}")

    def _do():
        result[0] = _hs(host, port, pw)

    t = threading.Thread(target=_do, daemon=True)
    t.start()

    dots, last_d = 0, pygame.time.get_ticks()
    while t.is_alive():
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
        now = pygame.time.get_ticks()
        if now - last_d > 400:
            dots = (dots + 1) % 4
            last_d = now
        _bg()
        msg = _fm.render("Verbinde" + "." * dots, True, (255, 255, 255))
        _sf.blit(msg, msg.get_rect(center=(_SW // 2, _SH // 2 - 30)))
        sub = _fs.render(f"{host}:{port}", True, (150, 150, 180))
        _sf.blit(sub, sub.get_rect(center=(_SW // 2, _SH // 2 + 24)))
        _ctx.present()
        _clk.tick(30)

    t.join()
    _bg()
    if result[0]:
        print("Connection successful")
        ok = _fm.render("OK", True, (60, 220, 90))
        _sf.blit(ok, ok.get_rect(center=(_SW // 2, _SH // 2)))
    else:
        print("Connection failed")
        fail = _fm.render("Verbindung fehlgeschlagen", True, (255, 80, 80))
        _sf.blit(fail, fail.get_rect(center=(_SW // 2, _SH // 2)))
    _ctx.present()
    pygame.time.wait(1100)
    return result[0]


def _run(path, tag, *a):
    print(f"Launching module: {tag} from {path}")
    mod = _load(path, tag)
    mod.main(*a)
    print("Module finished, returning to menu.")


def _err(text):
    print(f"Error: {text}")
    _bg()
    t = _fm.render(text, True, (255, 80, 80))
    _sf.blit(t, t.get_rect(center=(_SW // 2, _SH // 2)))
    _ctx.present()
    pygame.time.wait(1800)


def _online(host, port, pw):
    if not _conn_screen(host, port, pw):
        return
    if not os.path.isfile(_ONL):
        _err("online/main.py missing")
        return
    _run(_ONL, "game_onl", _ctx, host, port, _TK, pw)


def _local_flow():
    while True:
        action = _local_menu()
        if action is None:
            return
        if action[0] == "host":
            cfg = _host_config()
            if cfg is None:
                continue
            name, pw = cfg
            if _host_start(name, pw, _DEF_PORT) is None:
                _err("Hosting fehlgeschlagen")
                continue
            _online("127.0.0.1", _DEF_PORT, pw)
            return
        if action[0] == "manual":
            host, port, pw = _srv_input(local=True)
            if host is None:
                continue
            _online(host, port, pw)
            return
        _, ip, port, pw = action
        _online(ip, port, pw)
        return


def start():
    print("Launcher starting...\n")
    print("WARNING: This client is a beta verion please report bugs")

    if (_SO / _DT).exists():
        print()
    else:
        time.sleep(3)
        (_SO / _DT).touch()
        print()

    print("██╗     ██╗██████╗  ██████╗ ██╗  ██╗██████╗ ")
    print("██║    ███║██╔══██╗██╔═══██╗╚██╗██╔╝╚════██╗")
    print("██║    ╚██║██████╔╝██║   ██║ ╚███╔╝  █████╔╝")
    print("██║     ██║██╔══██╗██║   ██║ ██╔██╗  ╚═══██╗")
    print("███████╗██║██║  ██║╚██████╔╝██╔╝ ██╗██████╔╝")
    print("╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ \n")
    print("Welcome to the game engine! This engine was created by l1rox3.")
    print("Found a bug in the game engine? Contact me at my dev-mail:l1rox3-developer@gmail.com")
    _pf()
    _ui()

    while True:
        mode = _mode_sel()
        if mode is None:
            break
        if mode == "offline":
            _run(_OFF, "game_off", _ctx)
            continue
        if mode == "local":
            _local_flow()
            continue
        host, port, pw = _srv_input(local=False)
        if host is None:
            continue
        _online(host, port, pw)

    if _gs is not None:
        _gs.stop()
    print("Launcher shutting down.")
    pygame.quit()


if __name__ == "__main__":
    start()
