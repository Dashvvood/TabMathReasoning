import json
import threading
import queue
from gradio_client import Client
from omegaconf import OmegaConf

class LlamaClient:
    def __init__(self, urls, template=None):
        if not urls:
            raise ValueError("URLs list cannot be empty")
        self.urls = urls
        self.subclients = queue.Queue()
        for url in urls:
            self.subclients.put(Client(url))
        self.template = template or [
            {
                "role": "system",
                "content": (
                    "You are an expert assistant designed to provide concise and accurate answers to user queries."
                )
            },
            {
                "role": "user",
                "content": None  # Placeholder for the user's input
            }
        ]
        
    def submit(self, data, *args, **kwargs):
        results = []
        for item in data:
            text = item
            pid = 0
            client = self.subclients.get()  # 从队列中获取客户端
            result = self._submit_to_server(client, pid, text, *args, **kwargs)
            results.append((pid, result))
            self.subclients.put(client)  # 将客户端放回队列
        return results

    def _submit_to_server(self, client, pid, text, *args, **kwargs):
        message = self.template.copy()
        message[1]["content"] = text
        try:
            message = json.dumps(message)
        except json.JSONEncodeError as e:
            raise ValueError(f"Failed to serialize message: {e}")
        job = client.submit(message, *args, **kwargs)
        result = job.result()
        if result and len(result) > 0:
            return result[0]
        return None


if __name__ == "__main__":
    # 使用示例
    def main(urls=[]):
        try:
            client = LlamaClient(urls=urls)
            data = ["Hello, world!", "How are you?", "Goodbye!"] * 10
            results = client.submit(data)
            for result in results:
                print(result)
        except Exception as e:
            print(f"An error occurred: {e}")

    # 加载配置文件
    conf = OmegaConf.load("config.yaml")
    SERVERS = []
    PORTS = []
    for name, server in conf["servers"].items():
        SERVERS.append(f"http://{server['host']}:{server['port']}")
        PORTS.append(int(server['port']))

    # 运行并计时
    import time
    tic = time.time()
    main(urls=SERVERS)
    toc = time.time()
    print(f"Elapsed time: {toc - tic:.2f} seconds")