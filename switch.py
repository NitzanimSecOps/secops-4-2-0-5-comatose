from dataclasses import dataclass
import socket
import select

from ethernet import Ethernet

# Put your past code here
class Switch:
    def __init__(self, port_names: list[str]):
        pass

    def run(self) -> None:
        print("[*] Switch is running and listening for traffic...")
        port_by_socket = {port.sock: port for port in self.ports}
        all_sockets = list(port_by_socket)
       
        while True:
            readable_sockets, _, _ = select.select(all_sockets, [], [])

            for sock in readable_sockets:
                raw_frame = sock.recv(65535)
                incoming_port = port_by_socket[sock]
                self._process_frame(raw_frame, incoming_port)

    def _process_frame(self, frame: bytes, incoming_port: Port) -> None:
        pass


if __name__ == "__main__":
    switch = Switch(["veth_sw1", "veth_sw2"])
    switch.run()

