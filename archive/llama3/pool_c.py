import socket
import argparse

def request_port(hostname, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hostname, port))
    client.send(b"REQUEST_PORT")
    port = client.recv(1024).decode()
    client.close()
    return port

def release_port(hostname, serverport, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hostname, serverport))
    client.send(f"RELEASE_PORT {port}".encode())
    response = client.recv(1024).decode()
    client.close()
    return response

# 示例使用
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
    
    port = request_port(args.hostname, args.port)
    
    if port != "NO_PORT_AVAILABLE":
        print(f"Allocated port: {port}")
        # 模拟客户端使用端口
        # ...
        # 使用完毕后释放端口
        response = release_port(args.hostname, args.port, port)
        print(response)
    else:
        print("No ports available.")