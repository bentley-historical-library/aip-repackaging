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

The `aip_repackager.py` script requires a project CSV argument to be passed as `-p` [`--project_csv`]. This project CSV should contain, at minimum:

- A `uuid` column with the AIP's Archivematica UUID. This can be grabbed from either the automation-tools database or from Archivematica's Ingest tab.
- Either an `archival_object_uri` column, an `archival_object_link` column, or an `archival_object_id` with the appropriate identifier from ArchivesSpace.

Optionally, the CSV can contain an `accessrestrict` column that specifies the access policy in DSpace for the AIP's `objects.zip` bitstream. The value for this column should correspond to BHL access policy groups that have been configured using `DAPPr`. Standard options for the BHL's use of these scripts are: `bentley_only`, `um_users`, and `bentley_staff`. The CSV can also contain an `unpublish` column with a value of `True` for each AIP that should have its resulting ArchivesSpace digital object's `Publish` status set to unpublished.

`aip_repackager.py` also requires a filesystem base path for the Archivematica instance passed using `-f` of `--filesystem` for most actions. The filesystem base path should be of the form `/path/to/archivematica`. That directory is expected to contain an `aip_storage` directory (containing Archivematica AIPs) and an `aip_to_item-queue` directory, which will be used as the working directory for AIP repackaging. The `aip_to_item-queue` directory should further have a `TO-DO` directory and a `Doing` directory, which are the working directories that will be used by `aip_repackager.py`

```
archivematica
  aip_storage
    uuid1
    uuid2
    uuid3
  aip_to_item-queue
    Doing
    TO-DO
```

`aip_repackager.py` takes an additional set of arguments depending on the step in the workflow. A standard workflow consists of the following steps:

- Copy the entire AIP directory tree from AIP storage to a "TO-DO" directory and move the AIP folder or .7z to a "Doing" directory

`aip_repackager.py -p /path/to/project.csv -f /path/to/archivematica -c [--copy]`

- Repackage the AIPs into objects.zip and metadata.zip

`aip_repackager.py -p /path/to/project.csv -f /path/to/archivematica -r [--repackage]`

- Deposit AIPs to DSpace

`aip_repackager.py -p /path/to/project.csv -f /path/to/archivematica -d [--deposit] --handle HANDLE`

The `handle` argument must be supplied and must correspond to the collection that the AIPs will be deposited to.

Optional but useful arguments for depositing to DSpace include `--dspace INSTANCE_NAME` and `--aspace INSTANCE_NAME` with INSTANCE_NAME values corresponding to the names given to DSpace instances when configuring DAPPr and ASpace instances when configuring the bhlaspaceapiclient, respectively.

- Update ArchivesSpace with Digital Objects
`aip_repackager.py -p /path/to/project.csv -u [--update_aspace]`

Optional arguments for updating ArchivesSpace include `--unpublish` to unpublish all created digital objects and `--aspace INSTANCE_NAME` where INSTANCE_NAME corresponds to an ASpace instance configured using bhlaspaceapiclient. Note that the `-f [--filesystem]` argument is not required to update ArchivesSpace.

## Configuration
The AIP repackaging script takes an option `--config` argument with a path to a configuration file. This configuration file can be configured to set up default values that might be consistent across projects (such as `--filesystem`, `--aspace` instance name, `--dspace` instance name) and can further be configured to set up project specific configurations (such as the `--project_csv` and DSpace collection `--handle`) or to override default values. This can cut down significantly on the number of arguments that must be passed to `aip_repackager.py`. Using the below configuration with the following command:
`aip_repackager.py --config /path/to/config.cfg --project_name project1`

is equivalent to:

`aip_repackager.py -p /path/to/project1.csv -f /path/to/archivematica --aspace INSTANCE_NAME --dspace INSTANCE_NAME --handle /2027.42/1234 --accessrestrict bentley_only`

```
[defaults]
filesystem=/path/to/archivematica
aspace=INSTANCE_NAME
dspace=INSTANCE_NAME
accessrestrict=bentley_staff

[project1]
project_dir=/path/to/project_name
handle=/2027.42/1234
accessrestrict=bentley_only
```

Note that if conflicting arguments are supplied on the command line, in the defaults section of the configuration file, or in the project-specific section of the configuration file, the following is the order in which they will be used (i.e., if `--filesystem` is supplied on the command-line and a `--filesystem` is given in the defaults section of the configuration file, the value supplied on the command-line will be used)
1. Command line
2. Project-specific configuration
3. Default configuration
