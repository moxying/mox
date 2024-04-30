from modelscope.hub.api import HubApi
from modelscope.hub.git import GitCommandWrapper
from modelscope.hub.repository import Repository
import os
import tempfile
import shutil
import re
import datetime
import time

MODELSCOPE_ACCESS_TOKEN = os.environ["MODELSCOPE_ACCESS_TOKEN"]
MODELSCOPE_MODEL_ID = os.environ["MODELSCOPE_MODEL_ID"]
MODELSCOPE_MODEL_DIR = os.environ["MODELSCOPE_MODEL_DIR"]

api = HubApi()
api.login(MODELSCOPE_ACCESS_TOKEN)

try:
    api.delete_model(model_id=MODELSCOPE_MODEL_ID)
except Exception as err:
    print(f"err: {err}")
    pass

print(f"delete_model done, wait 5 seconds")
time.sleep(5)

model_id = MODELSCOPE_MODEL_ID
model_dir = MODELSCOPE_MODEL_DIR
lfs_suffix = ("*.zip",)
revision = "master"
commit_message = None
tag = None

files_to_save = os.listdir(model_dir)
ignore_file_pattern = []
api.create_model(model_id=model_id)

print(f"create_model done, wait 5 seconds")
time.sleep(5)

tmp_dir = tempfile.mkdtemp()
git_wrapper = GitCommandWrapper()
try:
    repo = Repository(model_dir=tmp_dir, clone_from=model_id)
    git_wrapper.checkout(tmp_dir, revision)
    files_in_repo = os.listdir(tmp_dir)
    for f in files_in_repo:
        if f[0] != ".":
            src = os.path.join(tmp_dir, f)
            if os.path.isfile(src):
                os.remove(src)
            else:
                shutil.rmtree(src, ignore_errors=True)
    for f in files_to_save:
        if f[0] != ".":
            if any(
                [re.search(pattern, f) is not None for pattern in ignore_file_pattern]
            ):
                continue
            src = os.path.join(model_dir, f)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(tmp_dir, f))
            else:
                shutil.copy(src, tmp_dir)
    if not commit_message:
        date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        commit_message = "[automsg] push model %s to hub at %s" % (model_id, date)
    if lfs_suffix is not None:
        lfs_suffix_list = [lfs_suffix] if isinstance(lfs_suffix, str) else lfs_suffix
        for suffix in lfs_suffix_list:
            repo.add_lfs_type(suffix)
    repo.push(
        commit_message=commit_message, local_branch=revision, remote_branch=revision
    )
    if tag is not None:
        repo.tag_and_push(tag, tag)
except Exception:
    raise
finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
