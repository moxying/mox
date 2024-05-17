import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import uuid
import logging
from enum import Enum

from core.comfyui.basic_client import BasicClient
from .model import *
from core.const import *
from core.models.common import WSEvent
from core.server.event import EventDispatcher
from core.config import ConfigMgr


class ComfyUIProgressName(Enum):
    SUBMIT_TASK = "任务提交绘图引擎"
    TASK_START = "绘图引擎任务开始执行"
    TASK_DOING = "绘图引擎任务执行中"  # prompt_json.keys()
    TASK_DONE = "绘图引擎任务执行结束"


class ComfyUIEventData(BaseModel):
    task_id: int
    progress_name: str
    progress_tip: Optional[str] = None
    progress_value: int
    progress_value_max: int
    node_id: Optional[str] = None
    node_progress_value: Optional[int] = None
    node_progress_value_max: Optional[int] = None
    err_msg: Optional[str] = None


class ComfyUIClient(BasicClient):
    def __init__(self) -> None:
        client_id = str(uuid.uuid4())
        super().__init__(client_id)

        # task scope
        self.task_id = None
        self.prompt_json = None
        self.nodes = []
        self.nodes_done = []
        self.cur_exec_node = None

    def _reset_task_info(self, nodes, task_id, prompt_json):
        self.task_id = task_id
        self.prompt_json = prompt_json
        self.nodes = nodes
        self.nodes_done = []
        self.cur_exec_node = None

    def _update_progress(self, event_data: ComfyUIEventData):
        EventDispatcher().dispatch_event(
            f"{EVENT_TYPE_INTERNAL_COMFYUI}_{event_data.task_id}",
            event_data,
        )

    def queue_prompt(self, task_id: int, prompt_json, result_image_node_id: str = None):

        self._reset_task_info(
            nodes=list(prompt_json.keys()), task_id=task_id, prompt_json=prompt_json
        )

        # queue
        prompt_id = self.post_prompt_api(prompt_json).prompt_id
        logging.debug(
            f"[comfyui]queue done, prompt_id: {prompt_id}, task_id: {task_id}"
        )
        self._update_progress(
            ComfyUIEventData(
                task_id=task_id,
                progress_name=ComfyUIProgressName.SUBMIT_TASK,
                progress_value=1,
                progress_value_max=1,
            )
        )

        # handle progress
        self._ws_handle_progress(prompt_id)

        # get result
        return self._get_target_node_images(prompt_id, result_image_node_id)

    def _ws_handle_progress(self, prompt_id: str):
        # setup websocket
        ws = websocket.WebSocket()
        server_address = ConfigMgr().get_conf("comfyui")["endpoint"]
        ws.connect(f"ws://{server_address}/ws?clientId={self.client_id}")
        logging.debug(f"[comfyui]ws connect done, client_id: {self.client_id}")

        # ws msg
        # execution_start
        # execution_cached
        # (executing + progress x n) or executing
        # executing && node==null
        while True:
            out = ws.recv()
            if not isinstance(out, str):
                continue  # previews are binary data
            message = json.loads(out)
            message_type = message["type"]
            match message_type:
                case "execution_start":
                    data = message["data"]
                    if data["prompt_id"] != prompt_id:
                        continue
                    logging.info(f"ws execute start: {prompt_id}")
                    self._update_progress(
                        ComfyUIEventData(
                            task_id=self.task_id,
                            progress_name=ComfyUIProgressName.TASK_START,
                            progress_value=1,
                            progress_value_max=1,
                        )
                    )
                    continue
                case "execution_cached":
                    data = message["data"]
                    if data["prompt_id"] != prompt_id:
                        continue
                    logging.debug(f"execution_cached: {data}")
                    self.nodes_done = data["nodes"]
                    continue
                case "executing":
                    data = message["data"]
                    node_id = data["node"]
                    if "prompt_id" in data and data["prompt_id"] != prompt_id:
                        continue
                    if node_id is None:
                        logging.debug(f"ws execute done: {prompt_id}")
                        # websocket miss?
                        # if len(self.nodes_done) != len(self.nodes):
                        #     raise Exception(
                        #         f"task status not expect, nodes_done: {self.nodes_done}, nodes: {self.nodes}"
                        #     )
                        self._update_progress(
                            ComfyUIEventData(
                                task_id=self.task_id,
                                progress_name=ComfyUIProgressName.TASK_DOING,
                                progress_tip=f"工作流执行完成",
                                progress_value=len(self.nodes),
                                progress_value_max=len(self.nodes),
                            )
                        )
                        break
                    logging.debug(f"ws execute doing: {prompt_id}, node_id: {node_id} ")

                    if self.cur_exec_node:
                        logging.debug(f"node {self.cur_exec_node} exec done")
                        self.nodes_done.append(self.cur_exec_node)
                    self.cur_exec_node = node_id

                    self._update_progress(
                        ComfyUIEventData(
                            task_id=self.task_id,
                            progress_name=ComfyUIProgressName.TASK_DOING,
                            progress_tip=f"节点{node_id}开始执行",
                            progress_value=len(self.nodes_done) + 1,
                            progress_value_max=len(self.nodes),
                        )
                    )
                    continue
                case "progress":
                    data = message["data"]
                    node_id = data["node"]
                    if data["prompt_id"] != prompt_id:
                        continue
                    logging.debug(f"progress: {data}")
                    self._update_progress(
                        ComfyUIEventData(
                            task_id=self.task_id,
                            progress_name=ComfyUIProgressName.TASK_DOING,
                            progress_tip=f"节点{node_id}执行中",
                            progress_value=len(self.nodes_done) + 1,
                            progress_value_max=len(self.nodes),
                            node_id=node_id,
                            node_progress_value_max=data["max"],
                            node_progress_value=data["value"],
                        )
                    )
                    continue
                case "executed":  # 节点有output
                    # {"type": "executed", "data": {"node": "11", "output": {"images": [{"filename": "ComfyUI_temp_igimx_00013_.png", "subfolder": "", "type": "temp"}]}, "prompt_id": "86534afa-32ee-4359-82af-00c29b484a21"}}
                    data = message["data"]
                    if data["prompt_id"] != prompt_id:
                        continue
                    logging.info(f"executed: {data}")
                    continue
                case "execution_error":
                    data = message["data"]
                    exception_message = data["exception_message"]
                    self._update_progress(
                        ComfyUIEventData(
                            task_id=self.task_id,
                            progress_name=ComfyUIProgressName.TASK_DOING,
                            progress_tip="执行失败",
                            progress_value=len(self.nodes_done) + 1,
                            progress_value_max=len(self.nodes),
                            err_msg=exception_message,
                        )
                    )
                    raise Exception(
                        f"ws execute error: {prompt_id}, exception_message:   {exception_message}"
                    )
                case _:
                    # TODO: add more
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
