import subprocess

from common import print_new_section

class UnmountS3:
    def __init__(self, postgres_string: str, juicefs_executable: str, mount_dir: str):
        self.postgres_string = postgres_string
        self.juicefs_executable = juicefs_executable
        self.mount_dir = mount_dir

    def run(self, uuid: str):
        self._unmount()
        self._destroy_s3(uuid)

    def _destroy_s3(self, uuid: str):
        print_new_section("Destroying S3")

        subprocess.run([
            self.juicefs_executable,
            "destroy",
            "--yes", # Don't ask for confirmation
            self.postgres_string,
            uuid
        ])



    def _unmount(self):
        print_new_section("Unmount")

        subprocess.run([
            self.juicefs_executable,
            "umount",
            self.mount_dir,
        ])