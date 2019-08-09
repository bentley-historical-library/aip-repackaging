# BHL AIP Repackager
Repackages AIPs for the Bentley Historical Library's Archivematica --> DSpace workflow

## Installation
The AIP repackaging scripts depend on the Bentley's DSpace API wrapper (DAPPr) and ArchivesSpace API wrapper (bhlaspaceapiclient).

```
pip install git+https://github.com/bentley-historical-library/DAPPr.git
pip install git+https://github.com/bentley-historical-library/bhlaspaceapiclient.git
pip install git+https://github.com/djpillen/aip-repackaging.git
```

## Use
This package installs a script, `aip_repacker.py`, that can be used to copy AIPs from Archivematia's AIP Storage into a working directory, split and repackage the AIPs into `metadata.zip` and `objects.zip`, upload the AIPs to DSpace, and update ArchivesSpace with digital objects.

The use of this tool is highly localized to practices at the BHL.

The `aip_repackager.py` script requires a project directory argument to be passed as the first argument. This project directory should be of the form `/path/to/projects/project_name` and should contain a CSV of the form `project_name.csv` that contains, at minimum:

- Either a `path` column or a `collection_id` column. The `path` value can be grabbed from the Archivematica automation-tools database. `collection_id` should be added for AIPs that have gone through the manual Archivematica workflow.
- A `uuid` column with the AIP's Archivematica UUID. This can be grabbed from either the automation-tools database or from Archivematica's Ingest tab.
- Either an `archival_object_uri` column, an `archival_object_link` column, or an `archival_object_id` with the appropriate identifier from ArchivesSpace.

Optionally, the CSV can contain an `accessrestrict` column that specifies the access policy in DSpace for the AIP's `objects.zip` bitstream. The value for this column should correspond to BHL access policy groups that have been configured using `DAPPr`. Standard options for the BHL's use of these scripts are: `bentley_only`, `um_users`, and `bentley_staff`

`aip_repackager.py` also requires a filesystem base path for the Archivematica instance passed using `-f` of `--filesystem` for most actions. The filesystem base path should be of the form `/path/to/archivematica`. That directory is expected to contain an `aip_storage` directory (containing Archivematica AIPs) and an `aip_to_item-queue` directory, which will be used as the working directory for AIP repackaging.

`aip_repackager.py` takes an additional set of arguments depending on the step in the workflow. A standard workflow consists of the following steps:

- Copy from AIP storage to a "TO-DO" directory

`aip_repackager.py /path/to/project/project_name -f /path/to/archivematica -c [--copy]`

- Get names for repackaging

`aip_repackager.py /path/to/project_name -f /path/to/archivematica -g [--get_names]`

- Move AIPs to a "Doing" directory

`aip_repackager.py /path/to/project_name -f /path/to/archivematica -m [--move_aips]`

- Repackage the AIPs

`aip_repackager.py /path/to/project_name -f /path/to/archivematica -r [--repackage]`

- Deposit AIPs to DSpace

`aip_repackager.py /path/to/project_name -f /path/to/archivematica -d [--deposit] --handle HANDLE`

The `handle` argument must be supplied and must correspond to the collection that the AIPs will be deposited to.

Optional but useful arguments for depositing to DSpace include `--dspace INSTANCE_NAME` and `--aspace INSTANCE_NAME` with INSTANCE_NAME values corresponding to the names given to DSpace instances when configuring DAPPr and ASpace instances when configuring the bhlaspaceapiclient respectively.

- Update ArchivesSpace with Digital Objects
`aip_repackager.py -p /path/to/project_name -u [--update_aspace]`

Option arguments for updating ArchivesSpace include `--unpublish` to unpublish the created digital objects (digital objects default to published) and `--aspace INSTANCE_NAME` where INSTANCE_NAME corresponds to an ASpace instance configured using bhlaspaceapiclient. Note that the `-f [--filesystem]` argument is not required to update ArchivesSpace.
