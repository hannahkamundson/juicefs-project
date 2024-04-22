import argparse

from mount import MountS3
from unmount import UnmountS3
from juicefs_bench import JuiceFSBench
from common import print_new_section


mount_dir = "/home/hannah/Documents/example-mnt/mnt1"
juicefs_executable = "/home/hannah/Documents/Repos/juicefs/juicefs"
postgres_string = "postgres://postgres@myjuicefs.cvosic8aio60.us-east-2.rds.amazonaws.com:5432/juicefs"


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
    
    # JuieFS Benchmark
    bench_parser = subparsers.add_parser("jfsbench", help="Run JuiceFS benchmark test")
    bench_parser.add_argument("--is-prod", action="store_true", help="Run for actual output")

    args = parser.parse_args()

    if args.command == "mounts3":
        print("Mounting for S3")
        mount_s3 = MountS3(postgres_string, juicefs_executable, mount_dir)
        uuid = mount_s3.run(args.name)
        print("UUID: " + uuid)

    elif args.command == "unmounts3":
        print("Unmounting S3")
        unmount_s3 = UnmountS3(postgres_string, juicefs_executable, mount_dir)
        unmount_s3.run(args.uuid)

    elif args.command == "jfsbench":
        print("Running JuiceFS bench")
        bench_cmd = JuiceFSBench(postgres_string, juicefs_executable, mount_dir)
        bench_cmd.run(args.is_prod)
        
    print_new_section("Finishing benchmarking")