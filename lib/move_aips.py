import os
import shutil


def move_aips(AIPRepackager):
    to_do_dir = os.path.join(AIPRepackager.aip_to_item_queue, "TO-DO")
    doing_dir = os.path.join(AIPRepackager.aip_to_item_queue, "Doing")

    for collection, uuids in AIPRepackager.project_metadata["collections_to_uuids"].items():
        collection_dir = os.path.join(to_do_dir, collection)
        for uuid in uuids:
            aip_name = AIPRepackager.project_metadata["uuids_to_names"][uuid]
            parseable_uuid = uuid.replace("-", "").strip()
            n = 4
            parts = [parseable_uuid[i:i+n] for i in range(0, len(uuid), n)]
            path_to_uuid = os.path.join(collection_dir, *parts)
            path_to_aip = os.path.join(path_to_uuid, aip_name)
            path_to_dst = os.path.join(doing_dir, aip_name)
            if os.path.exists(path_to_aip) and not os.path.exists(path_to_dst):
                print("MOVING {} TO {}".format(path_to_aip, path_to_dst))
                shutil.move(path_to_aip, path_to_dst)
