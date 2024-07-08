import os

def is_system_generated(file_name):
    system_generated_files = ['__init__.py', '__pycache__']
    for system_file in system_generated_files:
        if system_file in file_name:
            return True
    return file_name.endswith('.pyc')

def is_migration_file_or_dir(path):
    return 'migrations' in path

def get_all_code_files(root_folders):
    code_files = []
    for root_folder in root_folders:
        for root, dirs, files in os.walk(root_folder):
            # Ignore git directories and migration files or directories
            dirs[:] = [d for d in dirs if '.git' not in d and not is_migration_file_or_dir(d)]
            for file in files:
                if not is_system_generated(file) and '.git' not in root and not is_migration_file_or_dir(root):
                    code_files.append(os.path.join(root, file))
    return code_files

def write_code_to_txt(file_paths, output_txt):
    with open(output_txt, 'w') as txt_file:
        for file_path in file_paths:
            try:
                with open(file_path, 'r', errors='ignore') as code_file:
                    txt_file.write(f"File: {file_path}\n")
                    txt_file.write(code_file.read())
                    txt_file.write("\n\n" + "="*80 + "\n\n")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    root_folders = [
        r"E:\SmartCare-Surgery-System\appointments",
        r"E:\SmartCare-Surgery-System\authentication",
        r"E:\SmartCare-Surgery-System\billing",
        r"E:\SmartCare-Surgery-System\dashboards",
        r"E:\SmartCare-Surgery-System\home",
        r"E:\SmartCare-Surgery-System\smartcare"
    ]
    output_txt = 'all_code.txt'
    code_files = get_all_code_files(root_folders)
    write_code_to_txt(code_files, output_txt)
    print(f"Code from all files has been written to {output_txt}")
