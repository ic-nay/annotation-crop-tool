import os
import argparse

parser = argparse.ArgumentParser(
    prog="Annotation Cropper",
)

def main():
    args = parser.parse_args()
    print(args)
    parsed = parse_input(args)
    if parsed["type"] == "yaml":
        pass
    elif parsed["type"] == "single":
        pass
    # TODO: Add support for n directories, rather than just one
    
    pass

def parse_input(args:list):
    directories, categories = []
    if len(args["input"]) == 1:
        input = args["input"][0]
        #Case: data.yaml file
        if os.path.isfile(input):
            directories, categories = yaml_parse(input)
        elif os.path.isdir(input):
            found_directories = []
            # Search for either data.yaml or image+label directories
            with os.scandir(input) as dir_info:
                for entry in dir_info:
                    if entry.is_dir():
                        found_directories.append(entry.name)
                    #Case: found data.yaml file, same as above
                    elif entry.name == "data.yaml":
                        directories, categories = yaml_parse(input)
                        break
            # TODO: Make names of image and label directories flexible, rather than hard-coded
            if len(found_directories) == 2 and 'images' in found_directories and 'labels' in found_directories:
                directories = input
        else:
            parser.error(f"Input {input} is not a valid file or directory path")
        # 3. If it doesn't, then inspect its subdirectories
        #    3.1 Does it only have 2? Good!
        #    3.2 Does one contain images? Good!
        # 4. Begin iterating over every file in the image directory, and look for a correspondingly-named file in the other directory.
        # 5. Try to parse the corresponding file
        # 6. Crop and save the resulting files according to the user's preferences.
        return {
            "type":"yaml",
            "input_directories":directories,
            "categories":categories
        }

    elif len(args["input"]) == 2:
        if os.path.isfile(args["input"][0]) and os.path.isfile(args["input"][1]):
            return {
                "type":"single",
                "files":args["input"]
            }        
        # 1. Is one file an image?
        # 2. Is the other a text file?
        
        pass
    else:
        parser.error("A maximum of two parameters should be specified for the input")

def yaml_parse(file_path:str):
    try:
        import yaml
    except:
        print("Unable to find YAML library, please ensure that a Python YAML parsing library is installed and available under the \"yaml\" module name")
    try:
        with open(file_path) as file:
            yaml_file = yaml.load(file)
    except:
        print("Unable to parse YAML file, please ensure it is correctly formatted")
    
    return [yaml_file['train'], yaml_file['val'], yaml_file['test']], yaml_file['names']




if __name__ == "__main__":
    parser.add_argument("-i", "--input", required=True, help="""
    The files you wish to input, as one of the following:\n
    - A file path, pointing towards a data.yaml file
    - A directory path, pointing to a folder containing two subfolders, one with images, and another with corresponding label files (for example, your train folder)\n
    - Two file paths, for both an image and corresponding annotation file
    """, nargs="+")

    parser.add_argument("-o", "--output", required=True, nargs=1, help="The directory you would like your output to be returned into. Subdirectories will be created for each category.")
    
    parser.add_argument("-p", "--preserve-directories", action="store_true", help="Preserve directories in a scenario where images and annotations are split across multiple directories (i.e. test/train/validate).")

    parser.add_argument("--store-by-image", action="store_true", help="")

    parser.add_argument("--dump", action="store_true", help="Rather than neatly place all images in folders, just dump them directly into the specified directory.")

    main()