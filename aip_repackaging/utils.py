import configparser
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


def parse_config(config_file, project_name):
    if not os.path.exists(config_file):
        print("Config file not found at {}".format(config_file))
        sys.exit()
    else:
        config = configparser.RawConfigParser()
        config.read(config_file)
        sections = config.sections()
        if "defaults" in sections:
            default_values = {key: value for key, value in config["defaults"].items()}
        else:
            default_values = {}

        if project_name in sections:
            default_values.update({key: value for key, value in config[project_name].items()})
        else:
            print("project {} not found in config file {}".format(project_name, config_file))

        if "unpublish" in default_values:
            if default_values["unpublish"].lower() in ["t", "true", "y", "yes"]:
                default_values["unpublish"] = True
            else:
                default_values["unpublish"] = False

        return default_values


def parse_project_csv(AIPRepackager):
    project_metadata = {
            "uuids": [],
            "uuids_to_uris": {},
            "uuids_to_aip_names": {},
            "uuids_to_accessrestricts": {},
            "uuids_to_item_handles": {},
            "uuids_to_mivideo_ids": {},
            "uuids_to_unpublish": []
            }

    with open(AIPRepackager.project_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uuid = row["uuid"].strip()
            project_metadata["uuids"].append(uuid)
            project_metadata["uuids_to_uris"][uuid] = parse_archival_object_uri(row)
            if row.get("accessrestrict"):
                project_metadata["uuids_to_accessrestricts"][uuid] = row["accessrestrict"]
            if row.get("item_handle"):
                project_metadata["uuids_to_item_handles"][uuid] = row["item_handle"]
            if row.get("aip_name"):
                project_metadata["uuids_to_aip_names"][uuid] = row["aip_name"]
            if row.get("mivideo_ids"):
                project_metadata["uuids_to_mivideo_ids"][uuid] = [mivideo_id.strip() for mivideo_id in row["mivideo_ids"].split(";")]
            if row.get("unpublish"):
                if row["unpublish"].lower().strip() in ["t", "true", "y", "yes"]:
                    project_metadata["uuids_to_unpublish"].append(uuid)
    return project_metadata


def update_project_csv(AIPRepackager, updated_field=None):
    data = []
    with open(AIPRepackager.project_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if updated_field not in fieldnames:
            fieldnames.append(updated_field)
        for row in reader:
            uuid = row["uuid"].strip()
            row[updated_field] = AIPRepackager.project_metadata["uuids_to_{}s".format(updated_field)].get(uuid)
            data.append(row)

    with open(AIPRepackager.project_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(data)
