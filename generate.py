import argparse
import os

def generate_template_files(root: str, type_: str, target: str):
    # Define base directory and file paths based on type
    if type_ == "msg":
        package_name = f"{root}.msg"
        dir_path = os.path.join(root, "msg")
        file_paths = [os.path.join(dir_path, f"{target}.lcm")]
        file_stems = [target]
        
    elif type_ == "srv":
        package_name = f"{root}.srv.{target}"
        dir_path = os.path.join(root, "srv", target)
        file_paths = [
            os.path.join(dir_path, f"{target}_request.lcm"),
            os.path.join(dir_path, f"{target}_response.lcm")
        ]
        file_stems = [f"{target}_request", f"{target}_response"]
        
    elif type_ == "action":
        package_name = f"{root}.action.{target}"
        dir_path = os.path.join(root, "action", target)
        file_paths = [
            os.path.join(dir_path, f"{target}_goal.lcm"),
            os.path.join(dir_path, f"{target}_result.lcm"),
            os.path.join(dir_path, f"{target}_feedback.lcm")
        ]
        file_stems = [f"{target}_goal", f"{target}_result", f"{target}_feedback"]
        
    else:
        raise ValueError("Type must be one of 'msg', 'srv', or 'action'.")

    # Ensure the directories exist
    os.makedirs(dir_path, exist_ok=True)

    # Generate each file with the appropriate content
    for file_path, file_stem in zip(file_paths, file_stems):
        with open(file_path, "w") as file:
            file.write(f"package {package_name};\n\nstruct {file_stem} {{\n}}\n")
        print(f"Generated: {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate LCM template files.")
    parser.add_argument("root", type=str, help="The root package name.")
    parser.add_argument("type", type=str, choices=["msg", "srv", "action"], help="The message type.")
    parser.add_argument("target", type=str, help="The target message name.")
    args = parser.parse_args()
    
    generate_template_files(args.root, args.type, args.target)


if __name__ == "__main__":
    main()
