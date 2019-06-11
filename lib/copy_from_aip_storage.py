import os
import shutil


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
                dst_dirpath = os.path.join(collection_dir, uuid_base_dirname)
                print("COPYING {} TO {}".format(uuid_base_dirpath, dst_dirpath))
                shutil.copytree(uuid_base_dirpath, dst_dirpath)
