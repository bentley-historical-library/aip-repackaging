from bhlaspaceapiclient import ASpaceClient
from .utils import parse_deposited_aips_csv


def make_digital_object(title, handle, uuid, unpublish_dos):
    if unpublish_dos:
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
    deposited_aips = parse_deposited_aips_csv(AIPRepackager)
    aspace = ASpaceClient(AIPRepackager.aspace_instance)
    digital_object_post_uri = aspace.repository + "/digital_objects"
    for aip in deposited_aips:
        print("Updating {}".format(aip["archival_object_uri"]))
        archival_object = aspace.get_aspace_json(aip["archival_object_uri"])
        title = aspace.make_display_string(archival_object)
        digital_object = make_digital_object(title, aip["handle"], aip["uuid"], AIPRepackager.unpublish_dos)
        response = aspace.post_aspace_json(digital_object_post_uri, digital_object)
        digital_object_uri = response["uri"]
        digital_object_instance = make_digital_object_instance(digital_object_uri)
        archival_object["instances"].append(digital_object_instance)
        aspace.update_aspace_object(archival_object["uri"], archival_object)
