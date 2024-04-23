import json
import requests
import os
from typing import List, Optional
from pydantic import BaseModel


class UploadImageResponse(BaseModel):
    name: str
    subfolder: str
    type: str


class SystemStatsResponse(BaseModel):

    class System(BaseModel):
        os: str
        python_version: str
        embedded_python: bool

    class Device(BaseModel):
        name: str
        type: str
        index: int
        vram_total: int
        vram_free: int
        torch_vram_total: int
        torch_vram_free: int

    system: System
    devices: List[Device]


class GetPromptResponse(BaseModel):
    class ExecInfo(BaseModel):
        queue_remaining: int

    exec_info: ExecInfo


class PostPromptResponse(BaseModel):
    prompt_id: Optional[str] = None
    number: Optional[float] = None
    node_errors: Optional[object] = None
    errors: Optional[object] = None


class BasicClient:
    def __init__(self, server_address: str, client_id: str) -> None:
        self.client_id = client_id
        self.server_address = server_address
        self.session = requests.Session()

    def get_embeddings_api(self) -> List:
        resp = self.session.get(f"http://{self.server_address}/embeddings")
        if resp.status_code != 200:
            raise Exception(f"get_embeddings_api failed: {resp.json()}")
        return resp.json()

    def get_extensions_api(self) -> List:
        resp = self.session.get(f"http://{self.server_address}/extensions")
        if resp.status_code != 200:
            raise Exception(f"get_extensions_api failed: {resp.json()}")
        return resp.json()

    def upload_image_api(
        self,
        image: bytes,
        filename: str,
        overwrite: bool = None,
        type: str = None,
    ) -> UploadImageResponse:
        """
        upload_image_api

        overwrite: True or False or None
        type: input or temp or output
        """
        files = {"image": (filename, image)}
        if overwrite:
            files["overwrite"] = overwrite
        if type:
            files["type"] = type
        resp = self.session.post(
            f"http://{self.server_address}/upload/image",
            files=files,
        )
        if resp.status_code != 200:
            raise Exception(f"upload_image_api failed: {resp.json()}")
        return UploadImageResponse.model_validate(resp.json())

    def upload_mask_api(self):
        raise NotImplementedError()

    def view_image_api(
        self,
        filename: str,
        type: str = "output",
        subfolder: str = "",
        preview: str = None,  # TODO
        channel: str = None,  # TODO
    ) -> bytes:
        params = {
            "filename": filename,
            "type": type,
            "subfolder": subfolder,
        }

        resp = self.session.get(f"http://{self.server_address}/view", params=params)
        if resp.status_code != 200:
            raise Exception(f"view_image_api failed: {resp.json()}")
        return resp.content

    def view_metadata_api(self):
        raise NotImplementedError()

    def get_system_stats_api(self) -> SystemStatsResponse:
        resp = self.session.get(f"http://{self.server_address}/system_stats")
        if resp.status_code != 200:
            raise Exception(f"get_system_stats_api failed: {resp.json()}")
        return SystemStatsResponse.model_validate(resp.json())

    def get_prompt_api(self) -> GetPromptResponse:
        resp = self.session.get(f"http://{self.server_address}/prompt")
        if resp.status_code != 200:
            raise Exception(f"get_prompt_api failed: {resp.json()}")
        return GetPromptResponse.model_validate(resp.json())

    def get_object_info_api(self):
        resp = self.session.get(f"http://{self.server_address}/object_info")
        if resp.status_code != 200:
            raise Exception(f"get_object_info_api failed: {resp.json()}")
        return resp.json()

    def get_object_info_node_api(self, node_class: str):
        resp = self.session.get(
            f"http://{self.server_address}/object_info/{node_class}"
        )
        if resp.status_code != 200:
            raise Exception(f"get_object_info_node_api failed: {resp.json()}")
        return resp.json()

    def get_history_api(self, max_items: int = None):
        params = {}
        if max_items:
            params["max_items"] = max_items
        resp = self.session.get(f"http://{self.server_address}/history", params=params)
        if resp.status_code != 200:
            raise Exception(f"get_history_api failed: {resp.json()}")
        return resp.json()

    def get_history_by_prompt_id_api(self, prompt_id: str):
        resp = self.session.get(f"http://{self.server_address}/history/{prompt_id}")
        if resp.status_code != 200:
            raise Exception(f"get_history_api failed: {resp.json()}")
        return resp.json()

    def get_queue_api(self):
        resp = self.session.get(f"http://{self.server_address}/queue")
        if resp.status_code != 200:
            raise Exception(f"get_queue_api failed: {resp.json()}")
        return resp.json()

    def post_prompt_api(
        self,
        prompt_json,
        number: float = None,  # TODO
        front: float = None,  # TODO
        extra_data: any = None,  # TODO
    ) -> PostPromptResponse:
        p = {"prompt": prompt_json, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        resp = self.session.post(f"http://{self.server_address}/prompt", data=data)
        if resp.status_code != 200:
            raise Exception(
                f"post_prompt_api failed, status_code: {resp.status_code}, {resp}"
            )
        return PostPromptResponse.model_validate(resp.json())

    def post_queue_api(self):
        raise NotImplementedError()

    def post_interrupt_api(self):
        raise NotImplementedError()

    def post_free_api(self):
        raise NotImplementedError()

    def post_history_api(self):
        raise NotImplementedError()


if __name__ == "__main__":
    print(f"basic comfyui client test")
    os.makedirs("tmp", exist_ok=True)

    server_address = "127.0.0.1:8188"
    client_id = "test_client_id"
    basic_client = BasicClient(server_address=server_address, client_id=client_id)

    # get_embeddings
    embeddings: List = basic_client.get_embeddings_api()
    print(f"get_embeddings_api: {embeddings}\n")

    # get_extensions
    extensions: List = basic_client.get_extensions_api()
    print(f"get_extensions_api: {extensions}\n")

    # upload_image_api
    with open("test/testdata/1.png", "rb") as f:
        image = f.read()
        resp: UploadImageResponse = basic_client.upload_image_api(
            image=image, filename="1.png"
        )
        print(f"upload_image_api: {resp}\n")

    # upload_mask_api
    # TODO

    # view_image_api
    image = basic_client.view_image_api("1.png", "input", "")
    with open("tmp/1.png", "wb") as f:
        f.write(image)
    print(f"view_image_api done\n")

    # view_metadata_api
    # TODO

    # get_system_stats_api
    system_stats: SystemStatsResponse = basic_client.get_system_stats_api()
    print(f"get_system_stats_api: {system_stats}\n")

    #  get_prompt_api
    prompt: GetPromptResponse = basic_client.get_prompt_api()
    print(f"get_prompt_api: {prompt}\n")

    # get_object_info_api
    object_info = basic_client.get_object_info_api()
    print(f"get_object_info_api: {object_info.keys()}\n")

    # get_object_info_node_api
    object_info_node = basic_client.get_object_info_node_api("KSampler")
    print(f"get_object_info_node_api: {object_info_node}\n")

    # get_history_api
    history = basic_client.get_history_api()
    print(f"get_history_api: {history}\n")

    # get_history_by_prompt_id_api
    history = basic_client.get_history_by_prompt_id_api("123")
    print(f"get_history_by_prompt_id_api: {history}\n")

    # get_queue
    queue = basic_client.get_queue_api()
    print(f"get_queue: {queue}\n")

    # post_prompt_api
    prompt_json_str = """
{
  "3": {
    "inputs": {
      "seed": 506217942176358,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "v1-5-pruned-emaonly.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "6": {
    "inputs": {
      "text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "text, watermark",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""
    prompt_json = json.loads(prompt_json_str)
    resp: PostPromptResponse = basic_client.post_prompt_api(prompt_json=prompt_json)
    print(f"post_prompt_api: {resp.prompt_id}\n")
