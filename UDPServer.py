import asyncio
import socket
import time
import msgspec.msgpack
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

class UDPAsyncServer:
    host: str
    port: int
    socket_family: int
    socket_type: int
    clients_connected: dict[tuple[str, int], int] = {}
    ping_interval: int = 5

    def __init__(self, host, port, socket_family=socket.AF_INET, socket_type=socket.SOCK_DGRAM, ping_interval=5):
        self.host = host
        self.port = port
        self.socket_family = socket_family
        self.socket_type = socket_type
        self.ping_interval = ping_interval

    async def handle_client_status(self, client_socket: socket.socket, client_address: tuple, udp_message_type: UDPMessageTypes):
        if udp_message_type == UDPMessageTypes.PING:
            self.clients_connected[client_address] = int(time.time())
            print(f"Received PING from {client_address} : {self.clients_connected[client_address]}")
            client_socket.sendto(UDPMessageTypes.PONG.value, client_address)

    async def check_connected_clients(self):
        while True:
            clients_connected: dict[tuple[str, int], int] = self.clients_connected.copy()
            for client_address, last_ping in clients_connected.items():
                if int(time.time()) - last_ping > self.ping_interval:
                    del self.clients_connected[client_address]
                    print(f"Client {client_address} disconnected, remaining clients: {len(self.clients_connected)}")
            await asyncio.sleep(1)
           
                    
    async def run_server(self):
        print(f"Starting UDP server on {self.host}:{self.port}")
        client_socket: socket.socket = socket.socket(self.socket_family, self.socket_type)
        client_socket.bind((self.host, self.port))
        client_socket.setblocking(False)

        loop = asyncio.get_event_loop()
        while True:
            try:
                data, client_address = await loop.sock_recvfrom(client_socket, 1024)                
                udp_message_type = UDPMessageTypes.from_bytes(data)

                if udp_message_type:
                    await self.handle_client_status(client_socket, client_address, udp_message_type)
                else:
                    print(f"Received unknown message from {client_address}: {data}")

            except Exception as e:
                print(f"Error: {e}")


async def main():
    tasks: list[asyncio.Task] = []
    server = UDPAsyncServer("127.0.0.1", 8080,ping_interval=1)
    tasks.append(asyncio.create_task(server.run_server()))
    tasks.append(asyncio.create_task(server.check_connected_clients()))
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    asyncio.run(main())


    