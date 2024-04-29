import argparse
import os

from mount import MountS3, MountUplink
from unmount import UnmountS3
from juicefs_bench import JuiceFSBench
from common import print_new_section

mount_dir: str
juicefs_executable: str

user = os.getlogin()

if user == "hannah":
    mount_dir = "/home/hannah/Documents/example-mnt/mnt1"
    juicefs_executable = "/home/hannah/Documents/Repos/juicefs/juicefs"
elif user == "ubuntu": # prod
    mount_dir = "/home/ubuntu/my-mnt"
    juicefs_executable = "/home/ubuntu/code/juicefs/juicefs"
elif user == "hamorrar": 
    mount_dir = "/home/hamorrar/Documents/example-mnt/mnt1"
    juicefs_executable = "/home/hamorrar/Documents/Repos/juicefs/juicefs"
else:
    raise Exception("Specify your user for the paths")

postgres_string_s3 = "postgres://postgres@myjuicefs.cvosic8aio60.us-east-2.rds.amazonaws.com:5432/juicefss3"
postgres_string_uplink = "postgres://postgres@myjuicefs.cvosic8aio60.us-east-2.rds.amazonaws.com:5432/juicefsuplink"


if __name__ == '__main__':
    print_new_section("Starting benchmarking")

    parser = argparse.ArgumentParser(prog="JuiceFS Benchmarking")
    
    subparsers = parser.add_subparsers(dest="command", help="Sub command help")

    # Mount S3
    mount_s3_parser = subparsers.add_parser("mounts3", help="Format and mount S3")
    mount_s3_parser.add_argument("--name", type=str, help="The name for the JuiceFS format setup", required=True)
    
    # Unmount S3
    unmount_s3_parser = subparsers.add_parser("unmounts3", help="Unmount and delete S3")
    unmount_s3_parser.add_argument("--uuid", type=str, help="The UUID to delete", required=True)

    # Mount Uplink
    mount_uplink_parser = subparsers.add_parser("mountuplink", help="Format and mount Uplink")
    mount_uplink_parser.add_argument("--name", type=str, help="The name for the JuiceFS format setup", required=True)
    
    # JuieFS Benchmark
    bench_parser = subparsers.add_parser("jfsbench", help="Run JuiceFS benchmark test")
    bench_parser.add_argument("--is-prod", action="store_true", help="Run for actual output")
    bench_parser.add_argument("--run-new", action="store_true", help="Run Uplink if true; otherwise, run s3")

    args = parser.parse_args()

    if args.command == "mounts3":
        print("Mounting for S3")
        mount_s3 = MountS3(postgres_string_s3, juicefs_executable, mount_dir)
        uuid = mount_s3.run(args.name)
        print("UUID: " + uuid)

    elif args.command == "unmounts3":
        print("Unmounting S3")
        unmount_s3 = UnmountS3(postgres_string_s3, juicefs_executable, mount_dir)
        unmount_s3.run(args.uuid)

    elif args.command == "mountuplink":
        print("Mounting for uplink")
        mount_uplink = MountUplink(postgres_string_uplink, juicefs_executable, mount_dir)
        uuid = mount_uplink.run(args.name)
        print("UUID: " + uuid)

    elif args.command == "jfsbench":
        postgres_str: str
        mount: str
        if args.run_new:
            print("Running JuiceFS bench for Uplink")
            postgres_str = postgres_string_uplink
            mount = mount_dir
        else:
            print("Running JuiceFS bench for S3")
            postgres_str = postgres_string_s3
            mount = mount_dir

        # TODO: this needs to be changed per
        bench_cmd = JuiceFSBench(postgres_str, juicefs_executable, mount)
        bench_cmd.run(args.is_prod)
        
    print_new_section("Finishing benchmarking")