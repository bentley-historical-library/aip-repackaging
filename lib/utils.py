import csv


def parse_project_csv(AIPRepackager):
    project_metadata = {
            "collections_to_uuids": {},
            "uuids_to_names": {},
            "uuids_to_uris": {},
            "uuids_to_handles": {},
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

            if row.get("archival_object_uri"):
                project_metadata["uuids_to_uris"][uuid] = row["archival_object_uri"]
            elif row.get("archival_object_id"):
                project_metadata["uuids_to_uris"][uuid] = "/repositories/2/archival_objects/{}".format(row["archival_object_id"])
            elif row.get("archival_object_link"):
                archival_object_id = row["archival_object_link"].split("_")[-1]
                project_metadata["uuids_to_uris"][uuid] = "/repositories/2/archival_objects/{}".format(archival_object_id)

            if row.get("accessrestrict"):
                project_metadata["uuids_to_accessrestricts"][uuid] = row["accessrestrict"]

    return project_metadata


def create_deposited_aips_csv(AIPRepackager):
    data = []
    with open(AIPRepackager.project_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            uuid = row["uuid"].strip()
            row["handle"] = AIPRepackager.project_metadata["uuids_to_handles"][uuid]
            data.append(row)
    if "handle" not in fieldnames:
        fieldnames.append("handle")

    with open(AIPRepackager.deposited_aips_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def parse_deposited_aips_csv(AIPRepackager):
    aips = []
    with open(AIPRepackager.deposited_aips_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uuid = row["uuid"].strip()
            archival_object_uri = row["archival_object_uri"].strip()
            dspace_handle = row["handle"].strip()
            aips.append({
                        "archival_object_uri": archival_object_uri,
                        "uuid": uuid,
                        "handle": dspace_handle
                        })
    return aips
