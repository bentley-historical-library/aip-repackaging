import os
import subprocess


def copy_from_aip_storage(AIPRepackager):
    to_do_dir = os.path.join(AIPRepackager.aip_to_item_queue, "TO-DO")

    for collection, uuids in AIPRepackager.project_metadata["collections_to_uuids"].items():
        collection_dir = os.path.join(to_do_dir, collection)
        if not os.path.exists(collection_dir):
            os.makedirs(collection_dir)
        for uuid in uuids:
            uuid_base_dirname = uuid[:4]
            uuid_base_dirpath = os.path.join(AIPRepackager.aip_storage, uuid_base_dirname)
            if os.path.exists(uuid_base_dirpath):
                dst_dirpath = os.path.join(collection_dir)
                print("COPYING {} TO {}".format(uuid_base_dirpath, dst_dirpath))
                # https://github.com/artefactual/archivematica-storage-service/blob/3f21a96879103d6e550752770e344cff42cd919a/storage_service/locations/models/space.py#L508-L510
                cmd = [
                    'rsync', '-t', '-O', '--protect-args', '-vv',
                    '--chmod=Fug+rw,o-rwx,Dug+rwx,o-rwx',
                    '-r', uuid_base_dirpath, dst_dirpath
                    ]
                subprocess.check_call(cmd)
