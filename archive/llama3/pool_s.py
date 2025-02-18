import socket
import threading
from omegaconf import OmegaConf
import argparse

# 可用端口池
conf = OmegaConf.load("config.yaml")
SERVERS = []
PORTS = []
for name, server in conf["servers"].items():
    SERVERS.append(f"http://{server['host']}:{server['port']}")
    PORTS.append(int(server['port']))

available_ports = set(PORTS)
occupied_ports = set()

# 等待队列
waiting_clients = []

# 锁和条件变量
lock = threading.Lock()
port_available = threading.Condition(lock)

def handle_client(conn):
    try:
        # 接收客户端请求
        data = conn.recv(1024).decode()
        if data == "REQUEST_PORT":
            with lock:
                while not available_ports:
                    # 没有可用端口，加入等待队列
                    waiting_clients.append(conn)
                    port_available.wait()  # 等待端口可用
                port = available_ports.pop()
                occupied_ports.add(port)
                conn.send(str(port).encode())
        elif data.startswith("RELEASE_PORT"):
            port = int(data.split()[1])
            with lock:
                if port in occupied_ports:
                    occupied_ports.remove(port)
                    available_ports.add(port)
                    conn.send(b"PORT_RELEASED")
                    # 通知等待的客户端
                    if waiting_clients:
                        waiting_client = waiting_clients.pop(0)
                        port_available.notify()
                else:
                    conn.send(b"PORT_NOT_OCCUPIED")
    finally:
        conn.close()

def start_server(hostname="127.0.0.1", port=17700):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((hostname, port))
    server.listen(5)
    print(f"Port management service started on {hostname}:{port}...")
    while True:
        conn, addr = server.accept()
        print(f"Connected by {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hostname",
        type=str,
        default="127.0.0.1"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=17700,
    )
    
    args, missing = parser.parse_known_args()
    
    start_server(hostname=args.hostname, port=args.port)