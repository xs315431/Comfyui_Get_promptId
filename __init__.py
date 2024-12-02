from .get_promptId import GetPromptId
from .success_callback import SuccessCallback

# Define the mappings for your custom nodes
NODE_CLASS_MAPPINGS = {
    "GetPromptId": GetPromptId,
    "SuccessCallback": SuccessCallback
}

# Define human-readable names for your nodes (optional)
NODE_DISPLAY_NAME_MAPPINGS = {
    "GetPromptId": "Get Prompt_Id",
    "SuccessCallback": "Success Callback"
}

# Export the mappings for use by ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
