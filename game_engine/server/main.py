import sys, json, math, time, socket, random, hashlib, threading

TOKEN = "l1rox3:7Nk2QvPx9mZgE4wR:hx91"
HOST = "0.0.0.0"
PORT = 7331
DISC_PORT = 7332
W, H = 1900, 1000
TICK = 30
DEATH_MAX = 50
WECH_DELAY = 240

COLORS = [(60, 120, 255), (60, 220, 90), (240, 220, 60),
          (230, 90, 230), (240, 140, 40), (60, 220, 220)]
STARTS = [(W - 100, H - 100), (50, 50), (W // 2, H // 2),
          (50, H - 100), (W - 100, 50), (W // 2, 80)]


def auth_hash(pw):
    return hashlib.sha256((TOKEN + ":" + pw).encode()).hexdigest()


def ack_hash(pw):
    return hashlib.sha256((TOKEN + ":" + pw + ":ACK").encode()).hexdigest()


class GS:
    def __init__(self, name="Klotz Server", password="", host=HOST, port=PORT):
        self.name = name
        self.password = password
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.players = {}
        self.socks = {}
        self.nid = 1
        self.wech = {"active": False, "x": -100, "y": -100, "timer": 0}
        self.phase = "wait"
        self.winner = None
        self.running = True
        self.srv = None

    def open(self):
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.srv.bind((self.host, self.port))
        self.srv.listen(16)

    def run_bg(self):
        self.open()
        threading.Thread(target=self.accept_loop, daemon=True).start()
        threading.Thread(target=self.tick_loop, daemon=True).start()
        threading.Thread(target=self.beacon_loop, daemon=True).start()

    def start(self):
        self.open()
        print(f"server '{self.name}' up on {self.host}:{self.port} "
              f"(password={'yes' if self.password else 'no'})")
        threading.Thread(target=self.tick_loop, daemon=True).start()
        threading.Thread(target=self.beacon_loop, daemon=True).start()
        try:
            self.accept_loop()
        except KeyboardInterrupt:
            self.stop()
            print("server shutting down")

    def stop(self):
        self.running = False
        try:
            self.srv.close()
        except Exception:
            pass

    def accept_loop(self):
        while self.running:
            try:
                c, a = self.srv.accept()
            except OSError:
                break
            threading.Thread(target=self.handle, args=(c, a),
                             daemon=True).start()

    def beacon_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            beacon = json.dumps({"magic": "KLOTZ1", "name": self.name,
                                 "port": self.port, "pw": bool(self.password),
                                 "players": len(self.players)}).encode()
            try:
                s.sendto(beacon, ("255.255.255.255", DISC_PORT))
            except Exception:
                pass
            time.sleep(1.0)

    def recvn(self, c, n):
        b = b""
        while len(b) < n:
            d = c.recv(n - len(b))
            if not d:
                raise ConnectionError
            b += d
        return b

    def handle(self, c, a):
        try:
            c.settimeout(8)
            h = self.recvn(c, 64).decode().strip()
            if h != auth_hash(self.password):
                c.close()
                return
            c.sendall(ack_hash(self.password).encode())
            hbuf = b""
            while b"\n" not in hbuf:
                d = c.recv(4096)
                if not d:
                    raise ConnectionError
                hbuf += d
            line, buf = hbuf.split(b"\n", 1)
            m = json.loads(line)
            if m.get("t") != "hello":
                c.close()
                return
        except Exception:
            try:
                c.close()
            except Exception:
                pass
            return
        c.settimeout(None)
        name = str(m.get("name", "Spieler"))[:16]
        pid = self.register(c, name)
        print(f"player {pid} ({name}) joined from {a[0]}")
        try:
            while self.running:
                while b"\n" in buf:
                    ln, buf = buf.split(b"\n", 1)
                    self.on_msg(pid, ln)
                d = c.recv(4096)
                if not d:
                    break
                buf += d
        except Exception:
            pass
        self.remove(pid)

    def register(self, c, name):
        with self.lock:
            pid = self.nid
            self.nid += 1
            slot = (pid - 1) % len(STARTS)
            p = {"id": pid, "name": name, "color": list(COLORS[slot]),
                 "x": STARTS[slot][0], "y": STARTS[slot][1], "size": 20,
                 "alive": True, "dying": False, "dt": 0.0,
                 "death_timer": 0, "slot": slot, "evt": []}
            self.players[pid] = p
        wel = {"t": "welcome", "id": pid, "color": p["color"],
               "start": [p["x"], p["y"]], "w": W, "h": H}
        c.sendall((json.dumps(wel) + "\n").encode())
        with self.lock:
            self.socks[pid] = c
        return pid

    def remove(self, pid):
        with self.lock:
            c = self.socks.pop(pid, None)
            self.players.pop(pid, None)
        if c:
            try:
                c.close()
            except Exception:
                pass
        print(f"player {pid} left")

    def on_msg(self, pid, ln):
        try:
            m = json.loads(ln)
        except Exception:
            return
        if m.get("t") != "state":
            return
        with self.lock:
            p = self.players.get(pid)
            if not p or not p["alive"] or p["dying"]:
                return
            p["x"] = max(0, min(W - p["size"], int(m.get("x", p["x"]))))
            p["y"] = max(0, min(H - p["size"], int(m.get("y", p["y"]))))

    def reset(self):
        for p in self.players.values():
            s = p["slot"]
            p["x"], p["y"] = STARTS[s]
            p["size"] = 20
            p["alive"] = True
            p["dying"] = False
            p["dt"] = 0.0
            p["death_timer"] = 0
            p["evt"].append({"t": "event", "kind": "respawn",
                             "x": p["x"], "y": p["y"]})

    def collisions(self):
        act = [p for p in self.players.values()
               if p["alive"] and not p["dying"]]
        for i in range(len(act)):
            for j in range(i + 1, len(act)):
                a, b = act[i], act[j]
                if a["dying"] or b["dying"]:
                    continue
                dx = (a["x"] + a["size"] / 2) - (b["x"] + b["size"] / 2)
                dy = (a["y"] + a["size"] / 2) - (b["y"] + b["size"] / 2)
                if math.hypot(dx, dy) < (a["size"] + b["size"]) / 2:
                    tot = a["size"] + b["size"]
                    if random.random() < a["size"] / tot:
                        loser, win = b, a
                    else:
                        loser, win = a, b
                    loser["dying"] = True
                    loser["dt"] = 0.0
                    loser["death_timer"] = 0
                    win["size"] = int(win["size"] * 1.5)
                    print(f"{win['name']} besiegt {loser['name']}")

    def deaths(self):
        for p in self.players.values():
            if p["dying"]:
                p["death_timer"] += 1
                p["dt"] = p["death_timer"] / DEATH_MAX
                if p["death_timer"] >= DEATH_MAX:
                    p["dying"] = False
                    p["alive"] = False
                    p["dt"] = 1.0

    def wechsler(self):
        w = self.wech
        if w["active"]:
            for p in self.players.values():
                if not p["alive"] or p["dying"]:
                    continue
                cx = p["x"] + p["size"] / 2
                cy = p["y"] + p["size"] / 2
                if math.hypot(cx - w["x"], cy - w["y"]) < p["size"] / 2 + 14:
                    kind = random.choice(["speed", "grow"])
                    if kind == "grow":
                        p["size"] = int(p["size"] * 1.2)
                    else:
                        p["evt"].append({"t": "event", "kind": "speed"})
                    w["active"] = False
                    w["timer"] = 0
                    w["x"], w["y"] = -100, -100
                    break
        else:
            w["timer"] += 1
            if w["timer"] > WECH_DELAY:
                w["x"] = random.randint(60, W - 60)
                w["y"] = random.randint(60, H - 60)
                w["active"] = True
                w["timer"] = 0

    def tick(self):
        with self.lock:
            ps = self.players
            n = len(ps)
            if self.phase == "wait":
                if n >= 2:
                    self.reset()
                    self.phase = "play"
                    self.winner = None
                    print("match started")
            elif self.phase == "play":
                if n == 0:
                    self.phase = "wait"
                else:
                    self.collisions()
                    self.deaths()
                    self.wechsler()
                    act = [p for p in ps.values()
                           if p["alive"] and not p["dying"]]
                    dying = any(p["dying"] for p in ps.values())
                    if not dying and len(act) <= 1:
                        self.phase = "over"
                        w = act[0] if act else None
                        self.winner = ({"name": w["name"],
                                        "color": w["color"]} if w else None)
                        print(f"match over winner={self.winner}")
            elif self.phase == "over":
                if n == 0:
                    self.phase = "wait"
                    self.winner = None
            self.broadcast()

    def broadcast(self):
        w = self.wech
        keys = ("id", "name", "color", "x", "y", "size",
                "alive", "dying", "dt")
        world = {"t": "world", "phase": self.phase,
                 "players": [{k: p[k] for k in keys}
                             for p in self.players.values()],
                 "wech": {"active": w["active"], "x": w["x"], "y": w["y"]},
                 "winner": self.winner}
        data = (json.dumps(world) + "\n").encode()
        dead = []
        for pid, c in list(self.socks.items()):
            try:
                c.sendall(data)
                p = self.players.get(pid)
                if p and p["evt"]:
                    for e in p["evt"]:
                        c.sendall((json.dumps(e) + "\n").encode())
                    p["evt"] = []
            except Exception:
                dead.append(pid)
        for pid in dead:
            self.socks.pop(pid, None)
            self.players.pop(pid, None)

    def tick_loop(self):
        while self.running:
            self.tick()
            time.sleep(1.0 / TICK)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    name = sys.argv[2] if len(sys.argv) > 2 else "Klotz Server"
    pw = sys.argv[3] if len(sys.argv) > 3 else ""
    GS(name, pw, HOST, port).start()
