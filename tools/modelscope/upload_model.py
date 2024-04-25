from modelscope.hub.api import HubApi
import os

MODELSCOPE_ACCESS_TOKEN = os.environ["MODELSCOPE_ACCESS_TOKEN"]
MODELSCOPE_MODEL_ID = os.environ["MODELSCOPE_MODEL_ID"]
MODELSCOPE_MODEL_DIR = os.environ["MODELSCOPE_MODEL_DIR"]

api = HubApi()
api.login(MODELSCOPE_ACCESS_TOKEN)
api.push_model(
    model_id=MODELSCOPE_MODEL_ID,
    model_dir=MODELSCOPE_MODEL_DIR,
)
