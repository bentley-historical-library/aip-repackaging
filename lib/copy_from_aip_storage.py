import os
import shutil
import subprocess
from tqdm import tqdm

from .utils import update_project_csv


def copy_from_aip_storage(AIPRepackager):
    to_do_dir = os.path.join(AIPRepackager.aip_to_item_queue, "TO-DO")
    doing_dir = os.path.join(AIPRepackager.aip_to_item_queue, "Doing")
    for uuid in tqdm(AIPRepackager.project_metadata["uuids"], desc="Copying AIPs"):
        uuid_base_dirname = uuid[:4]
        uuid_base_dirpath = os.path.join(AIPRepackager.aip_storage, uuid_base_dirname)
        if os.path.exists(uuid_base_dirpath):
            # https://github.com/artefactual/archivematica-storage-service/blob/3f21a96879103d6e550752770e344cff42cd919a/storage_service/locations/models/space.py#L508-L510
            cmd = [
                'rsync', '-t', '-O', '--protect-args', '-vv',
                '--chmod=Fug+rw,o-rwx,Dug+rwx,o-rwx',
                '-r', uuid_base_dirpath, to_do_dir
                ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for uuid in tqdm(AIPRepackager.project_metadata["uuids"], desc="Moving AIPs"):
        parseable_uuid = uuid.replace("-", "").strip()
        n = 4
        parts = [parseable_uuid[i:i+n] for i in range(0, len(uuid), n)]
        path_to_uuid = os.path.join(to_do_dir, *parts)
        aip_name = os.listdir(path_to_uuid)[0]
        AIPRepackager.project_metadata["uuids_to_aip_names"][uuid] = aip_name
        path_to_aip = os.path.join(path_to_uuid, aip_name)
        path_to_dst = os.path.join(doing_dir, aip_name)
        if os.path.exists(path_to_aip) and not os.path.exists(path_to_dst):
            shutil.move(path_to_aip, path_to_dst)

    update_project_csv(AIPRepackager, updated_field="aip_name")
