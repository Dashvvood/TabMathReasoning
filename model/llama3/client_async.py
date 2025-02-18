import asyncio
import json
from gradio_client import Client
from omegaconf import OmegaConf

class LlamaClient:
    def __init__(self, urls, template=None):
        if not urls:
            raise ValueError("URLs list cannot be empty")
        self.urls = urls
        self.subclients = asyncio.Queue()
        for url in urls:
            self.subclients.put_nowait(Client(url))
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
        self.semaphore = asyncio.Semaphore(2 * len(urls))

    async def submit(self, data, *args, **kwargs):
        tasks = []
        for item in data:
            text = item
            pid = 0
            async with self.semaphore:
                client = await self.subclients.get()
                task = asyncio.create_task(self._submit_to_server(client, pid, text, *args, **kwargs))
                tasks.append(task)
                self.subclients.put_nowait(client)
        results = await asyncio.gather(*tasks)
        return results

    async def _submit_to_server(self, client, pid, text, *args, **kwargs):
        message = self.template.copy()
        message[1]["content"] = text,
        message = json.dumps(message)

        job = client.submit(message, *args, **kwargs)
        result = job.result()
        if result and len(result) > 0:
            return result[0]
        return None



if __name__ == "__main__":
    # 使用示例
    async def main(urls=[]):
        try:
            client = LlamaClient(urls=urls)
            data = ["Hello, world!", "How are you?", "Goodbye!"] * 10
            results = await client.submit(data)
            for result in results:
                print(result)
        except Exception as e:
            print(f"An error occurred: {e}")
        
    conf = OmegaConf.load("config.yaml")
    SERVERS = []
    PORTS = []
    for name, server in conf["servers"].items():
        SERVERS.append(f"http://{server['host']}:{server['port']}")
        PORTS.append(int(server['port']))

    import time
    tic = time.time()
    asyncio.run(main(urls=SERVERS))
    toc = time.time()
    print(f"Elapsed time: {toc - tic:.2f} seconds")