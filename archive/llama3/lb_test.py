import json
import aiohttp
import asyncio
import argparse
from omegaconf import OmegaConf
import random

class AsyncLlamaClient:
    def __init__(self, url, template=None):
        self.url = url
        
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

    async def submit(self, text):
        """异步发送请求到服务器"""
        message = self.template.copy()
        message[1]["content"] = text
        message = json.dumps(message)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={"data": message}) as response:
                result = await response.json()
                return result

    async def dry_run(self, text="Hello"):
        """异步测试请求"""
        result = await self.submit(text)
        return result["data"][0]


async def process_server(name, server, text):
    """异步处理单个服务器的 dry_run 请求"""
    url = f"http://{server['host']}:{server['port']}"
    client = AsyncLlamaClient(url)
    result = await client.dry_run(text)
    return (name, result)


async def load_balancing_test(servers, num_requests=10):
    """异步负载均衡测试"""
    tasks = []
    for i in range(num_requests):
        # 随机选择一个服务器
        server_name, server_config = random.choice(list(servers.items()))
        print(f"Sending request {i+1} to server: {server_name}")

        # 创建异步任务
        task = asyncio.create_task(process_server(server_name, server_config, text=f"Request {i+1}"))
        tasks.append(task)

    # 等待所有任务完成
    results = await asyncio.gather(*tasks)

    # 打印结果
    for name, result in results:
        print(f"Response from {name}: {result}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Single server URL for testing"
    )
    parser.add_argument(
        "--num-requests",
        type=int,
        default=10,
        help="Number of requests to simulate for load balancing test"
    )
    args = parser.parse_args()

    if args.url is not None:
        # 单服务器模式
        client = AsyncLlamaClient(args.url)
        res = await client.dry_run()
        print(f"Response from single server: {res}")
    else:
        # 多服务器模式（负载均衡测试）
        conf = OmegaConf.load("config.yaml")
        servers = conf["servers"]

        print(f"Starting load balancing test with {args.num_requests} requests...")
        await load_balancing_test(servers, num_requests=args.num_requests)


if __name__ == '__main__':
    asyncio.run(main())