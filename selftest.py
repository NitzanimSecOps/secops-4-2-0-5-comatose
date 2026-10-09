"""selftest.py — run your switch locally without a real network.

    python selftest.py          # run the example scenarios below
    VS Code: open this file, press F5 (Run and Debug), set breakpoints in switch.py.

Your switch binds real AF_PACKET sockets (and run() blocks on select), which need root +
veth interfaces. This fakes the sockets so your Switch constructs anywhere; instead of run(),
it feeds frames straight to _process_frame() and prints which ports each frame went out.
Edit the scenarios at the bottom or call send() with your own frames.
"""
import socket
import struct

from switch import Switch   # your solution

PORTS = ["p0", "p1", "p2"]   # referenced by index (0,1,2), matching this order

A = "02:00:00:00:00:0a"
B = "02:00:00:00:00:0b"
BROADCAST = "ff:ff:ff:ff:ff:ff"


def _mac(m):
    return bytes.fromhex(m.replace(":", ""))


def eth_frame(src_mac, dst_mac, ethertype=0x0800, payload=b"hello"):
    return _mac(dst_mac) + _mac(src_mac) + struct.pack("!H", ethertype) + payload


class _FakeSock:
    def __init__(self, *a, **k):
        self.sent = []

    def bind(self, *a, **k):
        pass

    def send(self, data):
        self.sent.append(data)
        return len(data)

    def setsockopt(self, *a, **k):
        pass

    def close(self):
        pass


def new_switch():
    """A Switch whose ports use fake sockets, so it runs with no real interfaces."""
    for name, val in (("AF_PACKET", 17), ("SOCK_RAW", 3)):
        if not hasattr(socket, name):
            setattr(socket, name, val)
    if not hasattr(socket, "htons"):
        socket.htons = lambda x: x
    socket.socket = lambda *a, **k: _FakeSock()
    return Switch(PORTS)


def send(sw, frame, port_index, label=""):
    """Feed one frame into the switch on a port (by index), and show where it forwarded."""
    before = [len(p.sock.sent) for p in sw.ports]
    print(f"\n>>> {label or 'send'}  (in on port {port_index} = {PORTS[port_index]})")
    sw._process_frame(frame, sw.ports[port_index])     # <-- your code runs here; breakpoint it
    forwarded = [PORTS[i] for i, p in enumerate(sw.ports) if len(p.sock.sent) > before[i]]
    print(f"    forwarded to: {forwarded or 'nobody'}")


if __name__ == "__main__":
    sw = new_switch()

    # Unknown destination (and broadcast) floods to every other port; the switch also learns
    # the source. Then a frame TO a learned MAC should go out only its port.
    send(sw, eth_frame(A, BROADCAST), 0, "A on p0, broadcast -> floods; switch learns A@p0")
    send(sw, eth_frame(B, A), 1, "B->A on p1 -> A known on p0, forwards only to p0; learns B@p1")
    send(sw, eth_frame(A, B), 0, "A->B on p0 -> B known on p1, forwards only to p1")

    print("\nExpected: #1 floods to p1,p2; #2 forwards only to p0; #3 forwards only to p1.")
    print("Edit the scenarios above, or call send(sw, eth_frame(src, dst), port_index, 'label').")
