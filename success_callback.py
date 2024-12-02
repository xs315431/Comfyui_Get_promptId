import requests

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
                "request_url": ("STRING",{"default": "http://localhost:8196"}),
                "image_url": ("STRING",{"default": "http://localhost:8196"}),
                "prompt_id": ("STRING",{"default": "example"})
            }
        }
    RETURN_TYPES = ("STRING",)  
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"  # The entry-point method for this node
    CATEGORY = "SuccessCallback"  # Category under which the node will appear in the UI

    def __init__(self):
        pass

    def execute(self,request_url,image_url,prompt_id):
        """

        """


        payload = {
            "urlImg": image_url,
            "promptId": prompt_id
        }
        print("image_url:{},prompt_id:{},request_url:{}".format(image_url,prompt_id,request_url))
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

NODE_CLASS_MAPPINGS = {
    "SuccessCallback": SuccessCallback
}
# 节点名称映射 类:节点名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetPromptId": "Success Callback"
}

    

