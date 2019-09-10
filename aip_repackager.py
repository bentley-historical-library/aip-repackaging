#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from lib.copy_from_aip_storage import copy_from_aip_storage
from lib.utils import parse_config, parse_project_csv
from lib.repackage_aips import repackage_aips
from lib.deposit_aips import deposit_aips
from lib.update_archivesspace import update_archivesspace


class AIPRepackager(object):
    def __init__(self, project_csv, filesystem=None, collection_handle=None, aspace_instance=None, dspace_instance=None, unpublish_dos=None, default_group=None):
        if not os.path.exists(project_csv):
            print("Project CSV {} not found".format(project_csv))
            sys.exit()

        if filesystem is not None:
            if not os.path.exists(filesystem):
                print("Filesystem base directory {} not found".format(filesystem))
                sys.exit()
            self.filesystem_base_dir = filesystem
            self.aip_storage = os.path.join(filesystem, "aip_storage")
            self.aip_to_item_queue = os.path.join(filesystem, "aip_to_item-queue")
            if not os.path.exists(self.aip_storage):
                print("AIP Storage location {} not found".format(self.aip_storage))
                sys.exit()
            if not os.path.exists(self.aip_to_item_queue):
                print("AIP to item queue location {} not found".format(self.aip_to_item_queue))
                sys.exit()

        self.project_csv = project_csv
        self.project_name = os.path.split(self.project_csv.rstrip("/"))[-1].split(".")[0]
        self.project_metadata = self.parse_project_csv()
        self.collection_handle = collection_handle
        self.aspace_instance = aspace_instance
        self.dspace_instance = dspace_instance
        self.unpublish_dos = unpublish_dos
        if default_group is not None:
            self.default_group = default_group
        else:
            self.default_group = "bentley_staff"

    def parse_project_csv(self):
        project_metadata = parse_project_csv(self)
        return project_metadata

    def copy_from_aip_storage(self):
        copy_from_aip_storage(self)

    def repackage_aips(self):
        repackage_aips(self)

    def deposit_aips(self):
        deposit_aips(self)

    def update_archivesspace(self):
        update_archivesspace(self)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Repackage an AIP for deposit to Deep Blue')
    parser.add_argument('-p', '--project_csv', help="Path to a project CSV")
    parser.add_argument('-f', '--filesystem', help="Filesystem base directory")
    parser.add_argument('-c', '--copy', action="store_true", help="Copy from AIP Storage")
    parser.add_argument('-r', '--repackage', action="store_true", help="Repackage AIPs")
    parser.add_argument('-d', '--deposit', action="store_true", help="Deposit AIPs to DSpace")
    parser.add_argument('-u', '--update_aspace', action="store_true", help="Update ArchivesSpace")
    parser.add_argument('--unpublish', action="store_true", default=False, help="Unpublish ArchivesSpace digital objects")
    parser.add_argument('--handle', help="DSpace collection handle")
    parser.add_argument('--dspace', help="DSpace instance")
    parser.add_argument('--aspace', help="ASpace instance")
    parser.add_argument('--accessrestrict', help="The default group to use if restrictions are present on an archival object")
    parser.add_argument('--config', help="Path to configuration file")
    parser.add_argument('--project_name', help="The name of the project in a configuration file")
    args = parser.parse_args()

    variable_args = ["project_csv", "filesystem", "handle", "aspace", "dspace", "unpublish", "accessrestrict"]
    if args.config:
        if not args.project_name:
            print("project name (--project_name) must be supplied along with config file")
            sys.exit()
        configured_values = parse_config(args.config, args.project_name)
        configured_values.update({key: value for key, value in vars(args).items() if key in variable_args and vars(args).get(key)})
    else:
        configured_values = {key: value for key, value in vars(args).items() if key in variable_args and vars(args).get(key)}

    if not configured_values.get("project_csv"):
        print("A project CSV must be specified")
        sys.exit()

    aip_repackager = AIPRepackager(
                        configured_values.get("project_csv"),
                        configured_values.get("filesystem"),
                        configured_values.get("handle"),
                        configured_values.get("aspace"),
                        configured_values.get("dspace"),
                        configured_values.get("unpublish"),
                        configured_values.get("accessrestrict")
                    )

    if (args.copy or args.repackage or args.deposit) and not configured_values.get("filesystem"):
        print("Filesystem base directory (-f/--filesystem) must be specified for this action")
        sys.exit()

    if args.copy:
        aip_repackager.copy_from_aip_storage()

    if args.repackage:
        aip_repackager.repackage_aips()

    if args.deposit:
        if not configured_values.get("handle"):
            print("Collection handle required to deposit AIPs")
            sys.exit()
        aip_repackager.deposit_aips()

    if args.update_aspace:
        aip_repackager.update_archivesspace()
