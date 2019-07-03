import csv
import os


def get_names_for_repackaging(AIPRepackager):
    to_do_dir = os.path.join(AIPRepackager.aip_to_item_queue, "TO-DO")
    for collection, uuids in AIPRepackager.project_metadata["collections_to_uuids"].items():
        collection_dir = os.path.join(to_do_dir, collection)
        for uuid in uuids:
            if uuid not in AIPRepackager.project_metadata["uuids_to_names"].keys():
                parseable_uuid = uuid.replace("-", "").strip()
                n = 4
                parts = [parseable_uuid[i:i+n] for i in range(0, len(uuid), n)]
                path_to_uuid = os.path.join(collection_dir, *parts)
                name = os.listdir(path_to_uuid)[0]
                AIPRepackager.project_metadata["uuids_to_names"][uuid] = name

    data = []
    with open(AIPRepackager.project_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if not row.get("name"):
                uuid = row["uuid"].strip()
                row["name"] = AIPRepackager.project_metadata["uuids_to_names"][uuid]
            data.append(row)

    if "name" not in fieldnames:
        fieldnames.append("name")

    with open(AIPRepackager.project_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
