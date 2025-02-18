from aiohttp import web
import aiohttp
import asyncio
from omegaconf import OmegaConf

# 加载配置文件
conf = OmegaConf.load("config.yaml")
SERVERS = []
for name, server in conf["servers"].items():
    SERVERS.append(f"http://{server['host']}:{server['port']}")

print(f"{SERVERS = }")

def get_server_by_ip(ip):
    """根据客户端 IP 分配服务器"""
    # 使用哈希算法将 IP 映射到服务器
    hash_value = hash(ip) % len(SERVERS)
    return SERVERS[hash_value]

async def handle_request(request):
    # 获取客户端 IP
    client_ip = request.remote

    # 根据客户端 IP 分配服务器
    server_url = get_server_by_ip(client_ip)
    target_url = f"{server_url}{request.rel_url}"

    # 打印转发信息
    print(f"Forwarding request from {client_ip} to: {target_url}")

    # 转发请求
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=request.method,
                url=target_url,
                headers=request.headers,
                data=await request.read(),
            ) as resp:
                # 打印响应状态
                print(f"Response from {target_url}: {resp.status}")

                # 返回响应
                headers = dict(resp.headers)
                body = await resp.read()
                return web.Response(body=body, status=resp.status, headers=headers)
        except Exception as e:
            # 打印错误信息
            print(f"Error forwarding request to {target_url}: {e}")
            return web.Response(status=500, text=f"Internal Server Error: {e}")

app = web.Application()
app.router.add_route('*', '/{path:.*}', handle_request)

if __name__ == '__main__':
    print("Starting reverse proxy server on port 17700...")
    web.run_app(app, port=17700)