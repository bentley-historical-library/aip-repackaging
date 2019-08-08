import csv
import os
import sys


def parse_archival_object_uri(row):
    if row.get("archival_object_uri"):
        return row["archival_object_uri"].strip()
    elif row.get("archival_object_id"):
        return "/repositories/2/archival_objects/{}".format(row["archival_object_id"].strip())
    elif row.get("archival_object_link"):
        archival_object_id = row["archival_object_link"].strip().split("_")[-1]
        return "/repositories/2/archival_objects/{}".format(archival_object_id)
    else:
        print("Archival object uri not found for {}".format(row["uuid"]))
        sys.exit()


def parse_project_csv(AIPRepackager):
    project_metadata = {
            "collections_to_uuids": {},
            "uuids_to_names": {},
            "uuids_to_uris": {},
            "uuids_to_accessrestricts": {}
            }

    with open(AIPRepackager.project_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("path"):
                path = row["path"]
                collection = path.split("/")[0]
                if collection not in project_metadata["collections_to_uuids"]:
                    project_metadata["collections_to_uuids"][collection] = []
            elif row.get("collection_id"):
                collection = row["collection_id"]
                if collection not in project_metadata["collections_to_uuids"]:
                    project_metadata["collections_to_uuids"][collection] = []
            uuid = row["uuid"].strip()
            project_metadata["collections_to_uuids"][collection].append(uuid)
            if row.get("name"):
                project_metadata["uuids_to_names"][uuid] = row["name"]
            project_metadata["uuids_to_uris"][uuid] = parse_archival_object_uri(row)
            if row.get("accessrestrict"):
                project_metadata["uuids_to_accessrestricts"][uuid] = row["accessrestrict"]
    return project_metadata


def create_deposited_aips_csv(AIPRepackager):
    headers = ["uuid", "archival_object_uri", "handle"]
    with open(AIPRepackager.deposited_aips_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)


def update_deposited_aips_csv(AIPRepackager, uuid, handle):
    if not os.path.exists(AIPRepackager.deposited_aips_csv):
        create_deposited_aips_csv(AIPRepackager)

    archival_object_uri = AIPRepackager.project_metadata["uuids_to_uris"][uuid]
    data = [uuid, archival_object_uri, handle]
    with open(AIPRepackager.deposited_aips_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data)


def parse_deposited_aips_csv(AIPRepackager):
    if not os.path.exists(AIPRepackager.deposited_aips_csv):
        return []
    else:
        aips = []
        with open(AIPRepackager.deposited_aips_csv, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uuid = row["uuid"].strip()
                archival_object_uri = parse_archival_object_uri(row)
                dspace_handle = row["handle"].strip()
                aips.append({
                            "archival_object_uri": archival_object_uri,
                            "uuid": uuid,
                            "handle": dspace_handle
                            })
        return aips
