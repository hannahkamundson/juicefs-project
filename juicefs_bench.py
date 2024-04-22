import subprocess

from common import print_new_section


class JuiceFSBenchResults:
    def __init__(self, num_files: int, block_size: str, file_size: str, write_files_per_second: str, read_files_per_second: str):
        self.num_files: int = num_files
        self.block_size: str = block_size

        # Calculate the file size
        self.file_size_num: int = int(file_size[:-1])
        self.file_size_unit: str = file_size[-1]
        self.file_size_str = file_size
        
        # Calculate write metrics
        write_split = write_files_per_second.split(" ")
        self.write_files_per_second_num: float = float(write_split[0])
        self.write_files_per_second_unit: str = write_split[1]
        self.write_files_per_second_str: str = write_files_per_second
        
        # Calculate read metrics
        read_split = read_files_per_second.split(" ")
        self.read_files_per_second_str = read_files_per_second
        self.read_files_per_second_num = float(read_split[0])
        self.read_files_per_second_unit = read_split[1]

        # Convert files/s to bytes/s
        file_size_in_mib: float
        if self.file_size_unit.upper() == "K":
            file_size_in_mib= self.file_size_num / (1 << 10)
        elif self.file_size_unit.upper() == "M":
             file_size_in_mib = self.file_size_num
        elif self.file_size_unit.upper() == "G":
            file_size_in_mib = self.file_size_num << 10
        else:
            raise ValueError("The file size must end in K, M, or G")
        
        self.write_mib_per_second: float = self.write_files_per_second_num*file_size_in_mib
        self.read_mib_per_second: float = self.read_files_per_second_num*file_size_in_mib

    def __str__(self) -> str:
        return f"{self.file_size_str},{self.file_size_num},{self.file_size_unit},{self.num_files},{self.block_size},{self.write_files_per_second_str},{self.write_files_per_second_num},{self.write_files_per_second_unit},{self.read_files_per_second_str},{self.read_files_per_second_num},{self.read_files_per_second_unit},{self.write_mib_per_second},{self.read_mib_per_second}"

# Make sure this matches the toString above
TITLE: str = "file_size_str,file_size_num,file_size_unit,num_files,block_size,write_fps_str,write_fps_num,write_fps_unit,read_fps_str,read_fps_num,read_fps_unit,write_mib_per_second,read_mib_per_second"

class JuiceFSBench:
    def __init__(self, postgres_string: str, juicefs_executable: str, mount_dir: str):
        self.postgres_string = postgres_string
        self.juicefs_executable = juicefs_executable
        self.mount_dir = mount_dir

    def run(self, is_prod: bool):
        # setup
        threads = 1 # Number of threads to run in parallel
        block_size = "1M" # Size of each I/O block
        file_sizes: list[str] # List of file sizes to run
        file_count: int # Number of files to generate per thread per file size
        if is_prod:
            file_sizes = [
                "1K", # PNG image (though they range)
                "10K", # JPG image (though they range)
                "50K", # 5 page PDF
                "100K", # single webpage
                "500K", # 50 page PDF
                "1M", # 1 minute MP3
                "10M", # Max size of an email
                "100M", # TODO What is this equivalent to?
                "500M", # Standard 720p 30 minute TV show
                "1G" # TODO What is this equivalent to?
                          ]
            file_count = 10
        else:
            # If we are just testing the output, just  keep it small
            file_sizes = ["10K", "1M"]
            file_count = 3

        # run and capture results
        results: list[JuiceFSBenchResults] = []
        for file_size in file_sizes:
            results.append(self._run_juicefs_bench(threads=threads,
                            small_file_size=file_size,
                            small_file_count=file_count,
                            big_file_size=0, # We aren't doing big files
                            block_size=block_size))
            
        print(TITLE)
        for result in results:
            print(result)

    def _run_juicefs_bench(self, 
                          threads: int, 
                          small_file_size: str, 
                          small_file_count: int, 
                          big_file_size: int, 
                          block_size: str) -> JuiceFSBenchResults:
        """
        Run a single benchmark test
        """
        print_new_section("JuiceFS Bench")

        output = subprocess.run([
            self.juicefs_executable,
            "bench",
            self.mount_dir,
            "--threads",
            str(threads),
            "--block-size",
            block_size,
            "--small-file-size",
            small_file_size,
            "--small-file-count",
            str(small_file_count),
            "--big-file-size",
            str(big_file_size)
        ], capture_output=True)

        found_item: bool = False
        write_value: str
        read_value: str

        for line in output.stdout.decode('utf-8').split('\n'):
            if found_item and "|" in line:
                parts = line.split("|")
                metric = parts[1].strip()
                if "Write small" in metric:
                    write_value = parts[2].strip()
                elif "Read small" in metric:
                    read_value = parts[2].strip()
            elif (not found_item) and "ITEM" in line:
                found_item = True

        return JuiceFSBenchResults(num_files=small_file_count*threads,
                                block_size=block_size,
                                file_size=small_file_size,
                                write_files_per_second=write_value,
                                read_files_per_second=read_value)