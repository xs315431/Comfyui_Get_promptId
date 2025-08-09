import requests
import socket
from transformers import set_seed
import sys
import requests
import os

# 获取当前taskid


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

    def execute(self, seed=None):
        """
        针对运行中的任务，获取运行中任务的prompt_id返回
        """
        if seed:
            set_seed(self.hash_seed(seed))
        try:
            local_ip = self.get_local_ip()
            port = self.get_local_port()
            url = f"http://{local_ip}:{port}/queue"
            response = requests.get(url)
            # 检查响应状态
            if response.status_code == 200:
                print("Response received successfully!")
                queue_running = response.json().get("queue_running")
                if queue_running and len(queue_running) > 0 and len(queue_running[0]) > 1:
                    print("Response Content in queue_running:",
                          queue_running[0][1])  # 打印响应内容
                    return (queue_running[0][1],)
                else:
                    return ("queue_running:[]",)
            else:
                print(
                    f"Failed to receive a successful response, status code: {response.status_code}")
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
        args = sys.argv
        if '--port' in args:
            port_index = args.index('--port')  # 获取 --port 的索引
            if port_index + 1 < len(args):  # 确保后面还有一个值
                # print(f"port有值{args[port_index + 1] }")
                return args[port_index + 1]  # 获取 --port 后面的值
            else:
                return '8188'
        else:
            return '8188'

# 流程控制，运行到此节点（在最末尾的节点） 表示执行成功，向后端发送成功消息，携带taskid 图片url


class SuccessCallback:
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
            "required": {
                "request_url": ("STRING", {"default": "http://localhost:8196"}),
                "image_url": ("STRING", {"default": "http://localhost:8196"}),
                "prompt_id": ("STRING", {"default": "example"})
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"  # The entry-point method for this node
    CATEGORY = "SuccessCallback"  # Category under which the node will appear in the UI

    def __init__(self):
        pass

    def execute(self, request_url, image_url, prompt_id):
        """

        """

        payload = {
            "urlImg": image_url,
            "promptId": prompt_id
        }
        print("image_url:{},prompt_id:{},request_url:{}".format(
            image_url, prompt_id, request_url))
        try:
            response = requests.post(request_url, json=payload)  # 发送POST请求
            response.raise_for_status()  # 如果响应状态码不是200，将抛出异常
            return (response.text,)  # 返回JSON格式的响应内容
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # 打印HTTP错误信息
            return (str(http_err),)
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")  # 打印其他请求错误信息
            return (str(err),)


# 视频文件上传，得到云存储链接
class UploadVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING",),  # 你的视频类型名可能不同，可替换
                "upload_url": ("STRING",),
                "request_field_name": ("STRING", {"default": "file"}),
            },
            "optional": {
                "additional_request_headers": ("DICT",)
            }
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("status_code", "result_text")

    FUNCTION = "execute"
    OUTPUT_NODE = True

    CATEGORY = "UploadVideo"

    def __init__(self):
        pass

    def execute(self, video_path,
                request_field_name,
                upload_url="https://localhost:8090/upload/uploadVideo",
                additional_request_headers=None):

        if not os.path.isfile(video_path):
            return (400, f"File not found: {video_path}")

        with open(video_path, 'rb') as video_file:
            file_name = os.path.basename(video_path)
            files = {
                # 关键修改：使用提取的文件名替代完整路径
                request_field_name: (file_name, video_file, "video/mp4")
            }

            response = requests.post(
                url=upload_url,
                files=files,
                headers=additional_request_headers,
                timeout=30  # 延长超时时间（原 3 秒太短，大文件易超时）
            )

            try:
                return (200, response.text)
            except Exception:
                # 非 JSON 时输出文本
                return (500, '{"code":200,"msg":"未知错误","data":None}')


NODE_CLASS_MAPPINGS = {
    "GetPromptId": GetPromptId,
    "SuccessCallback": SuccessCallback,
    "UploadVideo": UploadVideo
}

# 节点名称映射 类:节点名称,这里的key和上面的mappings做映射 默认是map中的名称，通过这里修改
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetPromptId": "Get Prompt_Id",
    "SuccessCallback": "Success Callback",
    "UploadVideo": "Upload Video(Aoc)"
}

# 节点名称映射 类:节点名称,这里的key和上面的mappings做映射 默认是map中的名称，通过这里修改
# NODE_DISPLAY_NAME_MAPPINGS = {
#     "UploadVideo": "Upload Video(Aoc)",
#     "GetPromptId": "Get PromptId(Aoc)",
#     "SuccessCallback": "Success Callback(Aoc)"
# }
