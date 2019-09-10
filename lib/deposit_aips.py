from bhlaspaceapiclient import ASpaceClient
from dappr import DAPPr
from datetime import datetime
import os
import re
import sys
from tqdm import tqdm

from .utils import update_project_csv


def determine_access_policy(dspace, project_metadata, uuid, default_group):
    if project_metadata["uuids_to_accessrestricts"].get(uuid):
        group_name = project_metadata["uuids_to_accessrestricts"][uuid]
    else:
        group_name = default_group

    if not dspace.groups.get(group_name):
        print("dappr configuration for group {} not found".format(group_name))
        sys.exit()
    else:
        group_info = dspace.groups[group_name]
        group_id = group_info["group_id"]
        group_description = group_info["description"]
        return {"group_id": group_id, "description": group_description}


def deposit_aips(AIPRepackager):
    doing_dir = os.path.join(AIPRepackager.aip_to_item_queue, "Doing")
    aspace = ASpaceClient(instance_name=AIPRepackager.aspace_instance, expiring="false")
    dspace = DAPPr(instance_name=AIPRepackager.dspace_instance)

    dspace_collection = dspace.get_handle(AIPRepackager.collection_handle)
    collection_id = dspace_collection["id"]
    dspace.logout()

    for uuid in tqdm(AIPRepackager.project_metadata["uuids"], desc="Depositing AIPs"):
        if uuid not in AIPRepackager.project_metadata["uuids_to_item_handles"]:
            name = AIPRepackager.project_metadata["uuids_to_aip_names"][uuid]
            if name.endswith(".7z"):
                name = re.sub(r"\.7z$", "", name).strip()
            tqdm.write("Depositing {}".format(name))
            # create a new instance each time to avoid timeouts
            dspace = DAPPr(instance_name=AIPRepackager.dspace_instance)
            aip_dir = os.path.join(doing_dir, name)
            archival_object_uri = AIPRepackager.project_metadata["uuids_to_uris"][uuid]
            archival_object = aspace.get_aspace_json(archival_object_uri)
            resource = aspace.get_aspace_json(archival_object["resource"]["ref"])

            if sorted(os.listdir(aip_dir)) != ["metadata.zip", "objects.zip"]:
                print("UNRECOGNIZED BITSTREAM IN {}".format(aip_dir))
                print(os.listdir(aip_dir))
                sys.exit()

            # description
            description = ""
            if aspace.find_note_by_type(archival_object, "odd"):
                description = aspace.find_note_by_type(archival_object, "odd")
            elif aspace.find_note_by_type(archival_object, "abstract"):
                description = aspace.find_note_by_type(archival_object, "abstract")

            # access
            accessrestrict = aspace.find_notes_by_type(archival_object, "accessrestrict")
            rights_access = ""
            restriction_end_date = ""
            if accessrestrict:
                rights_access = aspace.sanitize_title(aspace.find_note_by_type(archival_object, "accessrestrict"))
                restriction_end_date = aspace.get_restriction_end_date(archival_object)

            bitstream_restrictions = False
            if accessrestrict or AIPRepackager.project_metadata["uuids_to_accessrestricts"].get(uuid):
                bitstream_restrictions_metadata = determine_access_policy(dspace, AIPRepackager.project_metadata, uuid, AIPRepackager.default_group)
                bitstream_restrictions = True

            date_issued = str(datetime.now().year)
            relation = aspace.build_hierarchy(archival_object, delimiter="-")
            author = aspace.get_resource_creator(resource)
            title = aspace.make_display_string(archival_object)
            rights_copyright = "This content may be under copyright. Researchers are responsible for determining the appropriate use or reuse of materials. Please consult the collection finding aid or catalog record for more information."

            item_metadata = [
                {"key": "dc.title", "value": title},
                {"key": "dc.contributor.author", "value": author},
                {"key": "dc.date.issued", "value": date_issued},
                {"key": "dc.rights.copyright", "value": rights_copyright},
                {"key": "dc.relation.ispartofseries", "value": relation}
            ]

            if rights_access:
                item_metadata.append({"key": "dc.rights.access", "value": rights_access})
            if restriction_end_date:
                item_metadata.append({"key": "dc.date.open", "value": restriction_end_date})
            if description:
                item_metadata.append({"key": "dc.description.abstract", "value": description})

            item_dictionary = {"name": title}
            item = dspace.post_collection_item(collection_id, item_dictionary)
            item_id = item["id"]
            item_handle = item["handle"]

            dspace.put_item_metadata(item_id, item_metadata)
            dspace.logout()
            for subdir in os.listdir(aip_dir):
                dspace = DAPPr(instance_name=AIPRepackager.dspace_instance)
                path_to_subdir = os.path.join(aip_dir, subdir)
                if subdir == "objects.zip":
                    bitstream = dspace.post_item_bitstream(item_id, path_to_subdir)
                    bitstream_id = bitstream["id"]
                    bitstream["name"] = "objects.zip"
                    if bitstream_restrictions:
                        bitstream["description"] = bitstream_restrictions_metadata["description"]
                    else:
                        bitstream["description"] = "Archival materials."
                    dspace.put_bitstream(bitstream_id, bitstream)
                    if bitstream_restrictions:
                        bitstream_policy = [{"action": "READ", "rpType": "TYPE_CUSTOM", "groupId": bitstream_restrictions_metadata["group_id"]}]
                        dspace.put_bitstream_policy(bitstream_id, bitstream_policy)
                elif subdir == "metadata.zip":
                    bitstream = dspace.post_item_bitstream(item_id, path_to_subdir)
                    bitstream_id = bitstream["id"]
                    bitstream["name"] = "metadata.zip"
                    bitstream["description"] = "Administrative information. Access restricted to Bentley staff."
                    dspace.put_bitstream(bitstream_id, bitstream)
                    bitstream_policy = [{"action": "READ", "rpType": "TYPE_CUSTOM", "groupId": dspace.groups["bentley_staff"]["group_id"]}]
                    dspace.put_bitstream_policy(bitstream_id, bitstream_policy)
                dspace.logout()

            dspace = DAPPr(instance_name=AIPRepackager.dspace_instance)
            dspace.post_item_license(item_id)
            dspace.logout()

            tqdm.write("Deposited {} to {}".format(name, item_handle))
            AIPRepackager.project_metadata["uuids_to_item_handles"][uuid] = item_handle
            update_project_csv(AIPRepackager, updated_field="item_handle")
        else:
            tqdm.write("UUID {} already deposited".format(uuid))

    aspace.logout()
