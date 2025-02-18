import argparse
import logging
import subprocess
from omegaconf import OmegaConf

# 配置日志
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # 输出到终端
        logging.FileHandler("server.log")  # 保存到日志文件
    ]
)

# 解析命令行参数
parser = argparse.ArgumentParser(description="Run the application")
parser.add_argument('--config', type=str, default="./config.yaml", help='Path to the config file')
args, _ = parser.parse_known_args()

# 读取配置
conf = OmegaConf.load(args.config)
servers = conf["servers"]

# 存储所有子进程
processes = {}

# backends
proxy = OmegaConf.create()
proxy["backends"] = []

# 启动所有服务器
for name, server in servers.items():
    logging.info(f"Starting server: {name} on port {server['port']} with device cuda:{server['device']}")
    
    process = subprocess.Popen(
        [
            "python", "app.py", 
            "--port", str(server["port"]), 
            "--device", f"cuda:{server['device']}"
        ],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )
    
    processes[name] = process
    
    # proxy["backends"].append({
    #     "host": server["host"],
    #     "port": server["port"]
    # })

# with open("proxy.yaml", "w") as f:
#     OmegaConf.save(proxy, f)

# process = subprocess.Popen(
#     [
#         "proxy",
#         "--config", "proxy.yaml"
#     ],
#     stdout=subprocess.PIPE, 
#     stderr=subprocess.PIPE, 
#     text=True
# )

# processes["proxy"] = process



# 监听所有进程的输出
while processes:
    for name, process in list(processes.items()):
        # 读取子进程的输出（非阻塞）
        output = process.stdout.readline()
        
        if output:
            logging.info(f"[{name}] {output.strip()}")
        
        # 检查进程是否结束
        if process.poll() is not None:
            logging.warning(f"Server {name} exited with code {process.returncode}")
            processes.pop(name)
