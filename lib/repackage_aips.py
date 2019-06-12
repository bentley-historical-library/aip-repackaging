import os
import re
import subprocess
import shutil


def repackage_aips(AIPRepackager):
    doing_dir = os.path.join(AIPRepackager.aip_to_item_queue, "Doing")
    for uuid, name in AIPRepackager.project_metadata["uuids_to_names"].items():
        aip_dir = os.path.join(doing_dir, name)
        if os.path.exists(aip_dir):
            if name.endswith(".7z"):
                print("Unarchiving {}".format(aip_dir))
                cmd = [
                    "7za", "x", aip_dir, "-o{}".format(doing_dir)
                ]

                subprocess.check_call(cmd)

                name = re.sub(r"\.7z$", "", name).strip()
                aip_dir = os.path.join(doing_dir, name)

            print("Repackaging {}".format(name))
            aip_objects = os.path.join(aip_dir, "data", "objects")
            repackaged_objects = os.path.join(aip_dir, "objects")
            zipped_objects = os.path.join(aip_dir, "objects.zip")
            zipped_metadata = os.path.join(aip_dir, "metadata.zip")
            os.mkdir(repackaged_objects)
            for item in os.listdir(aip_objects):
                if item in ["metadata", "submissionDocumentation"]:
                    continue
                os.rename(
                    os.path.join(aip_objects, item),
                    os.path.join(repackaged_objects, item)
                )

            # zip objects
            cmd = [
                "7za", "a",
                "-bd",
                "-tzip",
                "-y",
                "-mtc=on",
                "-mmt=on",
                zipped_objects,
                repackaged_objects
            ]
            subprocess.check_call(cmd)
            shutil.rmtree(repackaged_objects)

            # zip metadata
            cmd = [
                "7za", "a",
                "-bd",
                "-tzip",
                "-y",
                "-mtc=on",
                "-mmt=on",
                "-x!" + os.path.join(name, "objects.zip"),
                zipped_metadata,
                aip_dir
            ]
            subprocess.check_call(cmd)

            for item in os.listdir(aip_dir):
                if item in ["objects.zip", "metadata.zip"]:
                    continue
                elif item == "data":
                    shutil.rmtree(os.path.join(aip_dir, item))
                elif item in ["bag-info.txt", "bagit.txt", "manifest-sha256.txt", "tagmanifest-md5.txt"]:
                    os.remove(os.path.join(aip_dir, item))
            print("{} repackaged".format(name))
