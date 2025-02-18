import json
import gradio_client
import argparse
from omegaconf import OmegaConf
import socket


`class LlamaClientPool:
    def __init__(self, serverhost, serverport, template=None):
        self.serverhost = serverhost
        self.serverport = serverport
        if template is None:
            self.template = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert assistant designed to provide concise and accurate answers to user queries. "
                    )
                },
                {
                    "role": "user",
                    "content": None  # Placeholder for the user's input
                }
            ]
        else:
            self.template = template 
        
        self.client = None


    def submit(self, text, *args, **kwargs):
        port = None
        try:
            port = self.request_port(self.serverhost, self.serverport)
            # print(f"url: http://{self.serverhost}:{port}")
            self.client = gradio_client.Client(f"http://{self.serverhost}:{port}")
            
            message = self.template.copy()
            message[1]["content"] = text
            message = json.dumps(message)
            res = self.client.submit(message, *args, **kwargs).result()[0]
            self.release_port(self.serverhost, self.serverport, port)
        except Exception as e:
            print(f"Error: {e}")
            res = None
        finally:
            if port is not None:
                self.release_port(self.serverhost, self.serverport, port)
        return res
    
    def dry_run(self, text="Hello", *args, **kwargs):
        return self.submit(text, *args, **kwargs)
    
    async def async_dry_run(self, text="Hello", *args, **kwargs):
        return await self.submit(text, *args, **kwargs)
    
    def request_port(self, hostname, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((hostname, port))
        client.send(b"REQUEST_PORT")
        port = client.recv(1024).decode()
        client.close()
        return port

    def release_port(self, hostname, serverport, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((hostname, serverport))
        client.send(f"RELEASE_PORT {port}".encode())
        response = client.recv(1024).decode()
        client.close()
        return response`


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--hostname",
        type=str,
        default="127.0.0.1",
        help="The hostname of the server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=17700,
        help="The port of the server"
    )
    args, missing = parser.parse_known_args()
    
    print(f"{args = }")
    print(f"{missing = }")
    
    L = LlamaClientPool(args.hostname, args.port)
    print(L.dry_run())
    