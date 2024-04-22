import json
import os
import subprocess

from common import print_new_section

class MountS3:
    def __init__(self, postgres_string: str, juicefs_executable: str, mount_dir: str):
        self.postgres_string = postgres_string
        self.juicefs_executable = juicefs_executable
        self.mount_dir = mount_dir

    def run(self, name:str) -> str:
        uuid = self._format_s3(name)
        self._mount()

        return  uuid
        

    def _format_s3(self, name: str) -> str:
        print_new_section("Formatting for S3")
        # Check we have the required env vars
        if "META_PASSWORD" not in os.environ:
            raise Exception("You need to set the postgres password in env var META_PASSWORD")

        # Mount it
        output = subprocess.run([
            self.juicefs_executable,
            "format",
            "--storage",
            "s3",
            "--bucket",
            "https://gateway.storjshare.io/juicefsbucket",
            "--access-key",
            os.environ["STORJ_ACCESS_KEY"],
            "--secret-key",
            os.environ["STORJ_SECRET_KEY"],
            self.postgres_string,
            name
        ], capture_output=True)

        # Get the JSON data so we can know the UUID
        stderr = output.stderr.decode('utf-8')
        start_index = stderr.index("{")
        # Find the ending index of "}"
        end_index = stderr.index("}") + 1

        # Extract the substring from start_index to end_index
        json_string = stderr[start_index:end_index]

        # Convert the substring to a JSON object
        json_data = json.loads(json_string)

        print("UUID: " + json_data.get("UUID"))

        return json_data.get("UUID")

    def _mount(self):
        print_new_section("Mounting")

        subprocess.run([
            self.juicefs_executable,
            "mount",
            self.postgres_string,
            self.mount_dir,
            "--background" # Run detached
        ])