import subprocess
import os
import argparse
import json

def print_new_section(output: str):
    print("---------------------------" + output + "-----------------------------")

mount_dir = "/home/hannah/Documents/example-mnt/mnt1"
juicefs_executable = "/home/hannah/Documents/Repos/juicefs/juicefs"
postgres_string = "postgres://postgres@myjuicefs.cvosic8aio60.us-east-2.rds.amazonaws.com:5432/juicefs"

def format_s3(name: str) -> str:
    print_new_section("Formatting for S3")
    # Check we have the required env vars
    if "META_PASSWORD" not in os.environ:
        raise Exception("You need to set the postgres password in env var META_PASSWORD")

    # Mount it
    output = subprocess.run([
        juicefs_executable,
        "format",
        "--storage",
        "s3",
        "--bucket",
        "https://gateway.storjshare.io/juicefsbucket",
        "--access-key",
        os.environ["STORJ_ACCESS_KEY"],
        "--secret-key",
        os.environ["STORJ_SECRET_KEY"],
        postgres_string,
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

def destroy_s3(uuid: str):
    print_new_section("Destroying S3")

    subprocess.run([
        juicefs_executable,
        "destroy",
        "--yes", # Don't ask for confirmation
        postgres_string,
        uuid
    ])

def mount():
    print_new_section("Mounting")

    subprocess.run([
        juicefs_executable,
        "mount",
        postgres_string,
        mount_dir,
        "--background" # Run detached
    ])

def unmount():
    print_new_section("Unmount")

    subprocess.run([
        juicefs_executable,
        "umount",
        mount_dir,
    ])


if __name__ == '__main__':
    """
    The process is
    (1) format juicefs
    (2) mount a folder
    (3) test
    (4) unmount the folder
    (5) delete the juicefs format
    """
    print_new_section("Starting benchmarking")

    parser = argparse.ArgumentParser(prog="JuiceFS Benchmarking")
    
    subparsers = parser.add_subparsers(dest="command", help="Sub command help")

    mount_s3_parser = subparsers.add_parser("mounts3", help="Format and mount S3")
    
    mount_s3_parser.add_argument("--name",
                        type=str,
                        help="The name for the JuiceFS format setup",
                        required=True)
    
    unmount_s3_parser = subparsers.add_parser("unmounts3", help="Unmount and delete S3")

    unmount_s3_parser.add_argument("--uuid",
                        type=str,
                        help="The UUID to delete",
                        required=True)

    args = parser.parse_args()

    if args.command == "mounts3":
        print("Mounting for S3")
        uuid = format_s3(args.name)
        mount()

    elif args.command == "unmounts3":
        print("Unmounting S3")
        # unmount() TODO
        destroy_s3(args.uuid)
    


    # unmount()

    # destroy_s3(uuid)

    print_new_section("Finishing benchmarking")