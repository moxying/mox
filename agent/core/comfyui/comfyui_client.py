import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import uuid
import logging

from core.comfyui.basic_client import BasicClient
from .model import *
from core.const import *
from core.models.common import WSEvent
from core.models.gen_image import *
from core.server.event import EventDispatcher
from core.config import ConfigMgr

NAME_SUBMIT_TASK = "任务提交ComfyUI"
NAME_TASK_NODE_CACHED = "节点任务使用缓存"
NAME_TASK_NODE_START = "节点任务执行"
NAME_TASK_NODE_DOING = "节点任务执行中"
NAME_TASK_DONE = "ComfyUI执行结束"
NAME_TASK_FAILED = "ComfyUI执行失败"


class ComfyUIClient(BasicClient):
    def __init__(self) -> None:
        client_id = str(uuid.uuid4())
        super().__init__(client_id)

    def _update_progress(self, event_data: ComfyUIEventData):
        EventDispatcher().dispatch_event(
            f"{EVENT_TYPE_INTERNAL_COMFYUI}_{event_data.task_uuid}",
            event_data,
        )

    def queue_prompt(self, task_uuid, prompt_json, result_image_node_id: str = None):

        # queue
        prompt_id = self.post_prompt_api(prompt_json).prompt_id
        logging.debug(
            f"[comfyui]queue done, prompt_id: {prompt_id}, task_uuid: {task_uuid}"
        )
        self._update_progress(
            ComfyUIEventData(
                task_uuid=task_uuid,
                progress_name=NAME_SUBMIT_TASK,
                progress_value_max=len(prompt_json.keys()) + 2,
            )
        )

        # handle progress
        self._ws_handle_progress(prompt_id, task_uuid, prompt_json)

        # get result
        return self._get_target_node_images(prompt_id, result_image_node_id)

    def _ws_handle_progress(self, prompt_id: str, task_uuid: str, prompt_json):
        # setup websocket
        ws = websocket.WebSocket()
        server_address = ConfigMgr().get_conf("comfyui")["endpoint"]
        ws.connect(f"ws://{server_address}/ws?clientId={self.client_id}")
        logging.debug(f"[comfyui]ws connect done, client_id: {self.client_id}")
        progress_value_max = len(prompt_json.keys()) + 2
        while True:
            out = ws.recv()
            if not isinstance(out, str):
                continue  # previews are binary data
            message = json.loads(out)
            message_type = message["type"]
            match message_type:
                case "status":
                    # {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 1}}}}
                    continue
                case "progress":
                    data = message["data"]
                    node_id = data["node"]
                    if data["prompt_id"] != prompt_id:
                        continue
                    self._update_progress(
                        ComfyUIEventData(
                            task_uuid=task_uuid,
                            progress_name=NAME_TASK_NODE_DOING,
                            progress_tip=f"节点编号{node_id}",
                            node_id=node_id,
                            node_progress_value_max=data["max"],
                            node_progress_value=data["value"],
                            progress_value_max=progress_value_max,
                        )
                    )
                case "executing":
                    data = message["data"]
                    node_id = data["node"]
                    if "prompt_id" in data and data["prompt_id"] != prompt_id:
                        continue
                    if node_id is None:
                        logging.info(f"ws execute done: {prompt_id}")
                        self._update_progress(
                            ComfyUIEventData(
                                task_uuid=task_uuid,
                                progress_name=NAME_TASK_DONE,
                                progress_value_max=progress_value_max,
                            )
                        )
                        break
                    logging.info(f"ws execute doing: {prompt_id}")
                    self._update_progress(
                        ComfyUIEventData(
                            task_uuid=task_uuid,
                            progress_name=NAME_TASK_NODE_START,
                            progress_tip=f"节点编号{node_id}",
                            node_id=node_id,
                            progress_value_max=progress_value_max,
                        )
                    )
                    continue

                case "executed":
                    # {"type": "executed", "data": {"node": "11", "output": {"images": [{"filename": "ComfyUI_temp_igimx_00013_.png", "subfolder": "", "type": "temp"}]}, "prompt_id": "86534afa-32ee-4359-82af-00c29b484a21"}}
                    continue
                case "execution_start":
                    logging.info(f"ws execute start: {prompt_id}")
                    continue
                case "execution_error":
                    data = message["data"]
                    exception_message = data["exception_message"]
                    self._update_progress(
                        ComfyUIEventData(
                            task_uuid=task_uuid,
                            progress_name=NAME_TASK_FAILED,
                            err_msg=exception_message,
                            progress_value_max=progress_value_max,
                        )
                    )
                    raise Exception(
                        f"ws execute error: {prompt_id}, exception_message:   {exception_message}"
                    )
                case "execution_cached":
                    data = message["data"]
                    logging.info(f"execution_cached: {data}")
                    if data["prompt_id"] != prompt_id:
                        continue
                    nodes = data["nodes"]
                    self._update_progress(
                        ComfyUIEventData(
                            task_uuid=task_uuid,
                            progress_name=NAME_TASK_NODE_CACHED,
                            progress_tip=f"节点任务使用缓存",
                            cached_nodes=nodes,
                            progress_value_max=progress_value_max,
                        )
                    )
                    continue
                case "crystools.monitor":
                    # data = message["data"]
                    # monitor_data = CrystoolsMonitor.model_validate(data)
                    # TODO
                    continue
                case _:
                    logging.debug(f"ws ignore message_type: {message_type}")
                    continue
        logging.debug(f"[comfyui]exex done, prompt_id: {prompt_id}")
        ws.close()

    def _get_target_node_images(self, prompt_id, node_id):
        logging.debug("[comfyui]_get_target_node_images")
        history = self.get_history_by_prompt_id_api(prompt_id)[prompt_id]
        node_output = history["outputs"][node_id]
        images_output = []
        if "images" in node_output:
            for image in node_output["images"]:
                image_data = self.view_image_api(
                    image["filename"], image["type"], image["subfolder"]
                )
                images_output.append(image_data)
        return images_output
