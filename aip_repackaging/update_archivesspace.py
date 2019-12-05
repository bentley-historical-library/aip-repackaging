from bhlaspaceapiclient import ASpaceClient
from tqdm import tqdm

from .utils import update_project_csv


def update_existing_digital_object(aspace, archival_object, handle, unpublish_do):
    existing_do_updated = False
    existing_do_uri = ""
    dos_without_file_versions = []
    for instance in archival_object.get("instances"):
        if instance["instance_type"] == "digital_object":
            digital_object_uri = instance["digital_object"]["ref"]
            digital_object = aspace.get_aspace_json(digital_object_uri)
            if not digital_object["file_versions"]:
                dos_without_file_versions.append(digital_object)
            elif handle in digital_object["file_versions"][0]["file_uri"]:
                existing_do_updated = True
                existing_do_uri = digital_object_uri
    if dos_without_file_versions and not existing_do_updated:
        do_to_update = dos_without_file_versions[0]
        do_to_update_uri = do_to_update["uri"]
        do_to_update["file_versions"] = [{
                                        'file_uri': handle,
                                        'xlink_show_attribute': "new",
                                        'xlink_actuate_attribute': "onRequest"
                                        }]
        if unpublish_do:
            do_to_update["publish"] = False
        else:
            do_to_update["publish"] = True
        aspace.update_aspace_object(do_to_update_uri, do_to_update)
        existing_do_updated = True
        existing_do_uri = do_to_update_uri
        if len(dos_without_file_versions) > 1:
            dos_to_delete = dos_without_file_versions[1:]
            for do_to_delete in dos_to_delete:
                aspace.delete_aspace_object(do_to_delete["uri"])
    return existing_do_updated, existing_do_uri


def make_digital_object(title, handle, uuid, unpublish_do):
    if unpublish_do:
        publish = False
    else:
        publish = True
    digital_object = {}
    digital_object["title"] = title
    digital_object["digital_object_id"] = uuid
    digital_object["publish"] = publish
    digital_object["file_versions"] = [{
                                    'file_uri': handle,
                                    'xlink_show_attribute': "new",
                                    'xlink_actuate_attribute': "onRequest"
                                    }]
    return digital_object


def make_digital_object_instance(digital_object_uri):
    instance = {'instance_type': 'digital_object',
                'digital_object': {'ref': digital_object_uri}}
    return instance


def update_archivesspace(AIPRepackager):
    aspace = ASpaceClient(AIPRepackager.aspace_instance)
    digital_object_post_uri = aspace.repository + "/digital_objects"
    for uuid in tqdm(AIPRepackager.project_metadata["uuids"], desc="Updating ArchivesSpace"):
        if AIPRepackager.unpublish_dos or uuid in AIPRepackager.project_metadata["uuids_to_unpublish"]:
            unpublish_do = True
        else:
            unpublish_do = False
        handle = AIPRepackager.project_metadata["uuids_to_item_handles"][uuid]
        archival_object_uri = AIPRepackager.project_metadata["uuids_to_uris"][uuid]
        archival_object = aspace.get_aspace_json(archival_object_uri)
        existing_do_updated, existing_do_uri = update_existing_digital_object(aspace, archival_object, handle, unpublish_do)
        if not existing_do_updated:
            title = aspace.make_display_string(archival_object)
            digital_object = make_digital_object(title, handle, uuid, unpublish_do)
            response = aspace.post_aspace_json(digital_object_post_uri, digital_object)
            digital_object_uri = response["uri"]
            AIPRepackager.project_metadata["uuids_to_digital_objects"][uuid] = digital_object_uri
            digital_object_instance = make_digital_object_instance(digital_object_uri)
            archival_object["instances"].append(digital_object_instance)
            aspace.update_aspace_object(archival_object["uri"], archival_object)
        else:
            AIPRepackager.project_metadata["uuids_to_digital_objects"][uuid] = existing_do_uri
    update_project_csv(AIPRepackager, "digital_object")
