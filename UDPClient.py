import asyncio
import socket
import time
from enum import Enum

class UDPMessageTypes(Enum):
    PAYLOAD = b'\x00'
    PING = b'\x01'
    PONG = b'\x02'

    @classmethod
    def from_bytes(cls, byte_value: bytes):
        for message_type in cls:
            if byte_value == message_type.value:
                return message_type
        return None

class UDPClient:
    host: str
    port: int
    socket_family: int
    socket_type: int
    ping_interval: int = 5
    last_ping_time: float = 0

    def __init__(self, host, port, socket_family=socket.AF_INET, socket_type=socket.SOCK_DGRAM, ping_interval=5):
        self.host = host
        self.port = port
        self.socket_family = socket_family
        self.socket_type = socket_type
        self.ping_interval = ping_interval

    async def send_ping(self, client_socket: socket.socket):
        while True:
            current_time = time.time()
            if current_time - self.last_ping_time > self.ping_interval:
                client_socket.sendto(UDPMessageTypes.PING.value, (self.host, self.port))
                self.last_ping_time = current_time
                print(f"Sent PING to {self.host}:{self.port}")
            await asyncio.sleep(1)

    async def receive_messages(self, client_socket: socket.socket):
        while True:
            data, _ = await asyncio.get_event_loop().sock_recvfrom(client_socket, 1024)
            udp_message_type = UDPMessageTypes.from_bytes(data)
            if udp_message_type == UDPMessageTypes.PONG:
                print("Received PONG from server")
            else:
                print(f"Received unknown message: {data}")

    async def run_client(self):
        client_socket: socket.socket = socket.socket(self.socket_family, self.socket_type)
        client_socket.setblocking(False)
        await asyncio.gather(
            self.send_ping(client_socket),
            self.receive_messages(client_socket)
        )

async def main():
    client = UDPClient("127.0.0.1", 8080, ping_interval=1)
    await client.run_client()

if __name__ == "__main__":
    asyncio.run(main())
