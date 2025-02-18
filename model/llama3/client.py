import json
import gradio_client
import argparse
from omegaconf import OmegaConf
import multiprocessing


class LlamaClient:
    def __init__(self, url, template=None):
        self.client = gradio_client.Client(url)
        
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

    def submit(self, text, *args, **kwargs):
        message = self.template.copy()
        message[1]["content"] = text
        message = json.dumps(message)
        job = self.client.submit(message, *args, **kwargs)
        return job
    
    def dry_run(self, text="Hello, how are you?"):
        job = self.submit(text=text, return_full_text=False, max_new_tokens=32, top_p=1, do_sample=True)
        return job.result()[0]
    

    
def process_server(name, server):
    """处理单个服务器的 dry_run 请求"""
    url = f"http://{server['host']}:{server['port']}"
    client = LlamaClient(url)
    result = client.dry_run()
    return (name, result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default=None,
    )
    args, missing = parser.parse_known_args()
    print(f"{args = }")
    print(f"{missing = }")
    
    if args.url is not None:
        # 单服务器模式
        L = LlamaClient(args.url)
        res = L.dry_run()
        print(res)
    else:
        # 多服务器模式
        conf = OmegaConf.load("config.yaml")
        servers = conf["servers"]
        
        # 创建进程池
        with multiprocessing.Pool(processes=len(servers)) as pool:
            # 使用进程池并行处理每个服务器
            results = pool.starmap(process_server, servers.items())
        
        # 打印结果
        for name, result in results:
            print(f"Server {name}: {result}")