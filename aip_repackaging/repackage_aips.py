import bagit
import os
import re
import subprocess
import shutil
import sys
from tqdm import tqdm


def repackage_aips(AIPRepackager):
    doing_dir = os.path.join(AIPRepackager.aip_to_item_queue, "Doing")
    for uuid in tqdm(AIPRepackager.project_metadata["uuids"], desc="Repackaging AIPs"):
        name = AIPRepackager.project_metadata["uuids_to_aip_names"][uuid]
        aip_dir = os.path.join(doing_dir, name)
        if os.path.exists(aip_dir):
            if name.endswith(".7z"):
                cmd = [
                    "7za", "x", aip_dir, "-o{}".format(doing_dir)
                ]

                subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                name = re.sub(r"\.7z$", "", name).strip()
                aip_dir = os.path.join(doing_dir, name)

            if not bagit.Bag(aip_dir).is_valid(fast=True):
                print("AIP BAG {} IS NOT VALID ACCORDING TO PAYLOAD OXUM".format(aip_dir))
                sys.exit()

            aip_objects = os.path.join(aip_dir, "data", "objects")
            repackaged_objects = os.path.join(aip_dir, "objects")
            zipped_objects = os.path.join(aip_dir, "objects.zip")
            zipped_metadata = os.path.join(aip_dir, "metadata.zip")
            os.mkdir(repackaged_objects)
            for item in os.listdir(aip_objects):
                if item in ["metadata", "MetaData", "submissionDocumentation"]:
                    continue
                os.rename(
                    os.path.join(aip_objects, item),
                    os.path.join(repackaged_objects, item)
                )

            # zip objects
            cmd = [
                "7za", "a",
                "-mx=0",
                "-bd",
                "-tzip",
                "-y",
                "-mtc=on",
                "-mmt=on",
                zipped_objects,
                repackaged_objects
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            shutil.rmtree(repackaged_objects)

            # zip metadata
            cmd = [
                "7za", "a",
                "-mx=0",
                "-bd",
                "-tzip",
                "-y",
                "-mtc=on",
                "-mmt=on",
                "-x!" + os.path.join(name, "objects.zip"),
                zipped_metadata,
                aip_dir
            ]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            for item in os.listdir(aip_dir):
                if item in ["objects.zip", "metadata.zip"]:
                    continue
                elif item == "data":
                    shutil.rmtree(os.path.join(aip_dir, item))
                elif item in ["bag-info.txt", "bagit.txt", "manifest-sha256.txt", "tagmanifest-md5.txt", "tagmanifest-sha256.txt"]:
                    os.remove(os.path.join(aip_dir, item))
