import requests
import socket
from transformers import set_seed
import sys
class GetPromptId:
    """
    A custom node for making API requests and processing responses.
    Attributes and class methods are defined to match the framework's expectations,
    similar to the provided Example node structure.
    """
    @classmethod
    def INPUT_TYPES(cls):
        """
        Define input parameters for the APIRequestNode.
        """
        return {
            "optional": {
                "seed": ("INT", {"default": 1, "min": 1, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING",)  # Output types: JSON response
    RETURN_NAMES = ("promt_id",)
    FUNCTION = "execute"  # The entry-point method for this node
    CATEGORY = "GetPromptId"  # Category under which the node will appear in the UI

    def __init__(self):
        pass
    def hash_seed(self, seed):
        import hashlib
        # Convert the seed to a string and then to bytes
        seed_bytes = str(seed).encode('utf-8')
        # Create a SHA-256 hash of the seed bytes
        hash_object = hashlib.sha256(seed_bytes)
        # Convert the hash to an integer
        hashed_seed = int(hash_object.hexdigest(), 16)
        # Ensure the hashed seed is within the acceptable range for set_seed
        return hashed_seed % (2**32)
    def execute(self,seed=None):
        """
        针对运行中的任务，获取运行中任务的prompt_id返回
        """
        if seed:
            set_seed(self.hash_seed(seed))
        try:
            local_ip=self.get_local_ip()
            port=self.get_local_port()
            url = f"http://{local_ip}:{port}/queue"
            response = requests.get(url)
            # 检查响应状态
            if response.status_code == 200:
                print("Response received successfully!")
                queue_running = response.json().get("queue_running")
                if queue_running and len(queue_running) > 0 and len(queue_running[0]) > 1:
                    print("Response Content in queue_running:", queue_running[0][1])  # 打印响应内容
                    return (queue_running[0][1],)
                else:
                    return ("queue_running:[]",)
            else:
                print(f"Failed to receive a successful response, status code: {response.status_code}")
                return (f"HTTP Error {response.status_code}",)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return (str(e),)
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            return ("Error parsing JSON response",)

    # 获取当前程序运行的ip地址
    def get_local_ip(self):
        # 获取主机名
        hostname = socket.gethostname()
        # 获取本地主机的 IPv4 地址
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    
    # 获取当前运行程序的端口号
    def get_local_port(self):
        # 打印所有传递的命令行参数
        # print("所有命令行参数:", sys.argv)
        args=sys.argv
        if '--port' in args:
            port_index = args.index('--port')  # 获取 --port 的索引
            if port_index + 1 < len(args):  # 确保后面还有一个值
                # print(f"port有值{args[port_index + 1] }")
                return args[port_index + 1]  # 获取 --port 后面的值
            else:
                return '8188'
        else:
            return '8188'
        
        
NODE_CLASS_MAPPINGS = {
    "GetPromptId": GetPromptId
}
# 节点名称映射 类:节点名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetPromptId": "Get Prompt_Id"
}

    

