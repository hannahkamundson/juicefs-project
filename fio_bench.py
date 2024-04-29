import subprocess
import re

from common import test_file_sizes, prod_file_sizes

class JuiceFSFioBenchResults:
    def __init__(self, filesizeNum,filesize,bandwidthNum,bandwidth,clatNum,clat,rw):
        self.filesizeNum = filesizeNum
        self.filesize = filesize
        self.bandwidthNum = bandwidthNum
        self.bandwidth = bandwidth
        self.clatNum = clatNum
        self.clat = clat
        self.rw = rw
    

    def __str__(self) -> str:
        return f"{self.rw},{self.filesizeNum},{self.filesize},{self.bandwidthNum},{self.bandwidth},{self.clatNum}.{self.clat}"

# Make sure this matches the toString above
TITLE: str = "mode,filesizeNum,file_size,bandwidthNum,bandwith,clatNum,clat"

class JuiceFSBenchFio:
    def __init__(self, mount_dir: str):
        self.mount_dir = mount_dir

    def run(self, is_prod: bool):
        # setup
        threads = 1 # Number of threads to run in parallel
        block_size = "10K" # Size of each I/O block
        file_sizes: list[str] # List of file sizes to run
        file_count: int # Number of files to generate per thread per file size
        # If we are just testing the output, just  keep it small
        file_sizes = ["10K", "1M"]
        file_count = 2

        # run and capture results
        modes = ["read", "write", "randread", "randwrite"]
        results: list[JuiceFSFioBenchResults] = []
        for file_size in file_sizes:
            for mode in modes:
                self._run_juicefsfio_bench(
                                file_size=file_size,
                                block_size=block_size, rw=mode)
                                # TODO undo all of the stuff below and make it work
                results.append(self._run_juicefsfio_bench(
                                file_size=file_size,
                                block_size=block_size, rw=mode))
            
        print(TITLE)
        for result in results:
            print(result)

    def _run_juicefsfio_bench(self, file_size: str, block_size: str, rw: str) -> JuiceFSFioBenchResults:
        """
        Run a single benchmark test
        """

        print(f"**********Running file size {file_size}")

        output = subprocess.run([
            "fio",
            "--name=fiorun"
            f"--directory={self.mount_dir}",
            "--ioengine=libaio",
            f"--rw={rw}", 
            f"--bs={block_size}", 
            f"--size={file_size}",
            "--numjobs=1",
            "--direct=1",
            "--group_reporting"
        ], capture_output=True)

        output_str = output.stdout.decode('utf-8')
        output_err = output.stderr.decode('utf-8')

        print(output_str)
        print(output_err)

        output_str = output.stdout.decode('utf-8')

        def split_string_between_letters_and_numbers(s):
            parts = re.findall(r'\d+\.\d+|\d+|[a-zA-Z/]+', s)
            return parts

        clat_match = re.search(r'avg=([\d.]+)', output_str)
        bw_match = re.search(r'BW=([\d.]+)', output_str)

        if clat_match and bw_match:
            clat = str(float(clat_match.group(1))) + "usec"
            bw = str(float(bw_match.group(1))) + "MiB/s"

            fs = split_string_between_letters_and_numbers(file_size)
            bwl = split_string_between_letters_and_numbers(bw)
            clatl = split_string_between_letters_and_numbers(clat)
            # print(clatl)

            # number, ogtext
            # print(fs[0] + "," + file_size + "," + bwl[0] + "," + bw + "," + clatl[0] + "," + clat)
            return JuiceFSFioBenchResults(filesizeNum=fs[0], filesize=file_size, bandwidthNum=bwl[0], bandwidth=bw, clatNum=clatl[0], clat=clat, rw=rw)