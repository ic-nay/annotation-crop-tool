from math import floor
import os
import argparse
import cv2

parser = argparse.ArgumentParser(
    prog="Annotation Cropper",
)

def main():
    args = parser.parse_args()
    input_object = parse_input(args)
    output_object = parse_output(args)
    if input_object["type"] == "yaml":
        # TODO: Add function to process "yaml" type objects (just creates a "directory" type object for each directory)
        process_yaml(input_object, output_object)
    elif input_object["type"] == "directory":
        # TODO: Add function to process "directory" type objects (iterate over every image file, find its matching label file, and then create a "single" type object to be passed to crop_and_save)
        process_directory(parsed, output_object)
    elif input_object["type"] == "single":
        print(crop_and_save(input_object, output_object))

def parse_input(args):

    # TODO: Add support for n directories, rather than just one

    directories, categories = ([], [])
    if len(args.input) == 1:
        input = args.input[0]
        #Case: data.yaml file
        if os.path.isfile(input):
            directories, categories = yaml_parse(input)
            return {
                "type":"yaml",
                "directories":directories,
                "categories":categories
            }
        elif os.path.isdir(input):
            directory_object = {
                "type":"directory",
                "image_directory":None,
                "label_directory":None,
                "categories":[]
            }
            # Search for either data.yaml or image+label directories
            with os.scandir(input) as dir_info:
                for entry in dir_info:
                    if entry.is_dir():
                        if entry.name == "images":
                            directory_object["image_directory"] = "images"
                        elif entry.name == "labels":
                            directory_object["label_directory"] = "labels"
                    #Case: found data.yaml file, same as above
                    elif entry.name == "data.yaml":
                        directories, categories = yaml_parse(input)
                        break
            # TODO: Make names of image and label directories flexible, rather than hard-coded
            if (directory_object["image_directory"] is not None) and (directory_object["label_directory"] is not None):
                return directory_object
        else:
            parser.error(f"Input {input} is not a valid file or directory path")
        # 3. If it doesn't, then inspect its subdirectories
        #    3.1 Does it only have 2? Good!
        #    3.2 Does one contain images? Good!
        # 4. Begin iterating over every file in the image directory, and look for a correspondingly-named file in the other directory.
        # 5. Try to parse the corresponding file
        # 6. Crop and save the resulting files according to the user's preferences.

    elif len(args.input) == 2:
        if os.path.isfile(args.input[0]) and os.path.isfile(args.input[1]):
            return {
                "type":"single",
                "files":args.input,
                "categories":None
            }
        else:
            parser.error("Invalid file")
    else:
        parser.error("A maximum of two parameters should be specified for the input")

def yaml_parse(file_path:str):
    try:
        import yaml
    except:
        print("Unable to find YAML library, please ensure that a Python YAML parsing library is installed and available under the \"yaml\" module name")
    try:
        with open(file_path) as file:
            yaml_file = yaml.safe_load(file)
    except:
        print("Unable to parse YAML file, please ensure it is correctly formatted")
    
    return [yaml_file['train'], yaml_file['val'], yaml_file['test']], yaml_file['names']

def parse_output(args):
    try:
        os.mkdir(args.output)
    except FileExistsError:
        return {
            "base_path":args.output
        }
    except:
        parser.error(f"Cannot create or open output directory {args.output}")
    return {
        "base_path":args.output
    }

def create_category_directories(base_dir, categories):
    print(categories)
    for category in categories:
        try:
            os.mkdir(os.path.join(base_dir, category))
        except FileExistsError:
            pass
        except:
            parser.error(f"Cannot create or open category directory {os.path.join(base_dir, category)}")

def parse_label_file(filepath, width, height) -> list:
    labels = []
    largest_category = 0
    with open(filepath) as file:
        for line in file:
            print(line)
            split_line = line.split(" ")
            if len(split_line) == 5:
                half_width = float(split_line[3])/2
                half_height = float(split_line[4])/2
                labels.append({
                    "category":int(split_line[0]),
                    "start_x": floor(width*(float(split_line[1]) - half_width)),
                    "start_y": floor(height*(float(split_line[2]) - half_height)),
                    "end_x" : floor(width*(float(split_line[1]) + half_width)),
                    "end_y" : floor(height*(float(split_line[2]) + half_height)),
                })
                if int(split_line[0]) > largest_category:
                    largest_category = int(split_line[0])
            else:
                return False
    return labels, largest_category

def crop_and_save(i, o) -> object:
    if i["categories"] is not None:
        categories = i["categories"]
    else:
        categories = None
    
    # Image and Label Loading

    print(i["files"][0])
    print("-"*25)
    print(i["files"][1])
    
    image = cv2.imread(i["files"][0])

    if image.size == 0:
        image = cv2.imread(i["files"][1])
        if image.size == 0:
            return {
                "result":False,
                "message":"No valid image file found",
                "files":i["files"]
            }
        else:
            labels, largest_category = parse_label_file(i["files"][0], width=image.shape[1], height=image.shape[0])
            if labels == False:
                return {
                    "result":False,
                    "message":"No valid label file found",
                    "files":i["files"]
                }
    else:
        labels, largest_category = parse_label_file(i["files"][1], width=image.shape[1], height=image.shape[0])
        if labels == False:
            return {
                "result":False,
                "message":"No valid label file found",
                "files":i["files"]
            }
    # Create necessary category directories
    if categories is not None and len(categories) == largest_category+1:
        create_category_directories(o["base_path"], categories)
    else:
        create_category_directories(o["base_path"], [str(i) for i in range(0, largest_category)])

    for label in labels:
        cropped_image = image[label["start_x"]:label["end_x"], label["start_y"]:label["end_y"]]
        try:
            category = categories[label["category"]]
        except:
            category = str(label["category"])
        directory = os.path.join(o["base_path"], category)
        id = 0
        filename = f"{os.path.splitext(os.path.basename(i["files"][0]))[0]}{id}.png"
        while os.path.isfile(os.path.join(directory, filename)):
            id += 1
            filename = f"{os.path.splitext(os.path.basename(i["files"][0]))[0]}_{id}.png"
        cv2.imwrite(os.path.join(directory, filename), cropped_image)
    
    return {
        "result": True,
        "message":"Successfully cropped and saved all resulting images",
        "files":i["files"]
    }


if __name__ == "__main__":
    parser.add_argument("-i", "--input", required=True, help="""
    The files you wish to input, as one of the following:\n
    - A file path, pointing towards a data.yaml file
    - A directory path, pointing to a folder containing two subfolders, one with images, and another with corresponding label files (for example, your train folder)\n
    - Two file paths, for both an image and corresponding annotation file
    """, nargs="+")

    parser.add_argument("-o", "--output", required=True, help="The directory you would like your output to be returned into. Subdirectories will be created for each category.")
    
    parser.add_argument("-v", "--verbose", action="store_true")

    parser.add_argument("-p", "--preserve-directories", action="store_true", help="Preserve directories in a scenario where images and annotations are split across multiple directories (i.e. test/train/validate).")

    parser.add_argument("--store-by-image", action="store_true", help="")

    parser.add_argument("--dump", action="store_true", help="Rather than neatly place all images in folders, just dump them directly into the specified directory.")

    main()