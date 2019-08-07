#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from lib.copy_from_aip_storage import copy_from_aip_storage
from lib.utils import parse_project_csv
from lib.get_names_for_repackaging import get_names_for_repackaging
from lib.move_aips import move_aips
from lib.repackage_aips import repackage_aips
from lib.deposit_aips import deposit_aips
from lib.update_archivesspace import update_archivesspace


class AIPRepackager(object):
    def __init__(self, project_dir, filesystem=None, collection_handle=None, aspace_instance=None, dspace_instance=None, unpublish_dos=None):
        if not os.path.exists(project_dir):
            print("Project directory {} not found".format(project_dir))
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

        self.project_dir = project_dir
        self.project_name = os.path.split(self.project_dir)[-1]
        self.project_csv = os.path.join(self.project_dir, "{}.csv".format(self.project_name))
        if not os.path.exists(self.project_csv):
            print("Project CSV {} not found".format(self.project_csv))
            sys.exit()
        self.deposited_aips_csv = os.path.join(self.project_dir, "deposited_aips.csv")
        self.project_metadata = self.parse_project_csv()
        self.collection_handle = collection_handle
        self.aspace_instance = aspace_instance
        self.dspace_instance = dspace_instance
        self.unpublish_dos = unpublish_dos

    def parse_project_csv(self):
        project_metadata = parse_project_csv(self)
        return project_metadata

    def copy_from_aip_storage(self):
        copy_from_aip_storage(self)

    def get_names_for_repackaging(self):
        get_names_for_repackaging(self)

    def move_aips(self):
        move_aips(self)

    def repackage_aips(self):
        repackage_aips(self)

    def deposit_aips(self):
        deposit_aips(self)

    def update_archivesspace(self):
        update_archivesspace(self)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Repackage an AIP for deposit to Deep Blue')
    parser.add_argument('-p', '--project_dir', help="Project directory")
    parser.add_argument('-f', '--filesystem', help="Filesystem base directory")
    parser.add_argument('-c', '--copy', action="store_true", help="Copy from AIP Storage")
    parser.add_argument('-g', '--get_names', action="store_true", help="Get names for repackaging")
    parser.add_argument('-m', '--move_aips', action="store_true", help="Move AIPs")
    parser.add_argument('-r', '--repackage', action="store_true", help="Repackage AIPs")
    parser.add_argument('-d', '--deposit', action="store_true", help="Deposit AIPs")
    parser.add_argument('-u', '--update_aspace', action="store_true", help="Update ArchivesSpace")
    parser.add_argument('--unpublish', action="store_true", default=False, help="Unpublish ArchivesSpace digital objects")
    parser.add_argument('--handle', help="DSpace collection handle")
    parser.add_argument('--dspace', help="DSpace instance")
    parser.add_argument('--aspace', help="ASpace instance")
    args = parser.parse_args()
    aip_repackager = AIPRepackager(
                        args.project_dir,
                        args.filesystem,
                        args.handle,
                        args.aspace,
                        args.dspace,
                        args.unpublish
                    )

    if args.copy:
        aip_repackager.copy_from_aip_storage()

    if args.get_names:
        aip_repackager.get_names_for_repackaging()

    if args.move_aips:
        aip_repackager.move_aips()

    if args.repackage:
        aip_repackager.repackage_aips()

    if args.deposit:
        if not args.handle:
            print("Collection handle required to deposit AIPs")
            sys.exit()
        aip_repackager.deposit_aips()

    if args.update_aspace:
        aip_repackager.update_archivesspace()
