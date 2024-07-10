import os
import zipfile
import time
import subprocess

def get_file_size(file_path):
    return os.path.getsize(file_path)

def estimate_compressed_size(file_paths, compression_level):
    # Simple estimation: Compression ratio often ranges from 30% to 70%
    total_size = sum(get_file_size(file) for file in file_paths)
    estimated_size = total_size * (1 - (compression_level / 9) * 0.4)  # 0.4 is an arbitrary compression ratio
    return estimated_size

def create_zip(directory, ignore_list, compression_level):
    with zipfile.ZipFile('minigame.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
        for root, dirs, files in os.walk(directory):
            # Ignore folders and files in the ignore list
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_list]
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in ignore_list:
                    zipf.write(file_path, os.path.relpath(file_path, directory))

def get_next_release_version(previous_release_file):
    if os.path.exists(previous_release_file):
        with open(previous_release_file, 'r') as f:
            previous_release = f.read().strip()
            major, minor, patch = map(int, previous_release.split('.'))
            next_release = f"{major}.{minor}.{patch + 1}"
    else:
        next_release = '1.0.0'
    
    with open(previous_release_file, 'w') as f:
        f.write(next_release)

    return next_release

if __name__ == "__main__":
    directory = os.getcwd()  # Automatically choose the current working directory

    # List of folders and files to ignore
    ignore_list = [
        os.path.join(directory, '.git'),
        os.path.join(directory, '__pycache__'),  # Example: add any other folder or file you want to ignore
        os.path.join(directory, 'minigame.mcworld')  # Example: add any specific file to ignore
    ]
    
    file_paths = []
    for root, dirs, files in os.walk(directory):
        # Ignore folders and files in the ignore list
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_list]
        for file in files:
            file_path = os.path.join(root, file)
            if file_path not in ignore_list:
                file_paths.append(file_path)
    
    compression_level = int(input("Enter compression level (1-9, where 9 is maximum compression): "))
    
    estimated_size = estimate_compressed_size(file_paths, compression_level)
    print(f"Estimated compressed size: {estimated_size / (1024 * 1024):.2f} MB")
    
    create_zip(directory, ignore_list, compression_level)
    print("minigame.zip has been created successfully.")
    
    # Wait for 2 seconds
    time.sleep(2)
    
    # Rename the zip file to mcworld
    try:
        os.rename('minigame.zip', 'minigame.mcworld')
        print("minigame.zip has been renamed to minigame.mcworld.")
    except FileExistsError:
        os.remove('minigame.mcworld')
        os.rename('minigame.zip', 'minigame.mcworld')
        print("Existing minigame.mcworld has been replaced with the new one.")
    
    # Git push and release publishing
    next_release_version = get_next_release_version('release_version.txt')
    print(f"Preparing to push and publish release {next_release_version}...")
    
    # Perform Git operations
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'Release v{next_release_version}'])
    subprocess.run(['git', 'tag', f'v{next_release_version}'])
    subprocess.run(['git', 'push'])
    subprocess.run(['git', 'push', '--tags'])
    
    print(f"Released version {next_release_version} successfully.")
