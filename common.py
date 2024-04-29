def print_new_section(output: str):
    print("---------------------------" + output + "-----------------------------")

prod_file_sizes = [
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

test_file_sizes = ["10K", "1M"]