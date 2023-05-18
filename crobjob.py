# cronjob 35 23 * * * python3 /home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/cronjob.py

import os
import requests

# Define the GitHub repository owner and name
repository_owner = "openxla"
repository_name = "iree"

# Define the script to execute upon new release
script_path = "/home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/mainscript.py"
# Define the local path where the tar file will be saved
local_tar_path = "/home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/iree-dist-20230517.522-linux-x86_64.tar.xz"


# Function to check for new pre-releases
def check_new_pre_release():
    api_url = f"https://api.github.com/repos/{repository_owner}/{repository_name}/releases"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        for release in response_json:
            if release["prerelease"]:
                pre_release_tag = release["tag_name"]
                if pre_release_tag != get_stored_version():
                    download_pre_release(release)
                    # Maybe this can be potential BUG, beaware!
                    #update_stored_version(pre_release_tag)
                    break
    else:
        print("Failed to retrieve pre-releases information.")

# Function to download the pre-release
def download_pre_release(release):
    assets = release["assets"]
    for asset in assets:
        download_url = asset["browser_download_url"]
        if download_url.endswith(".tar.xz"):
            # Check if the local tar file exists
            if os.path.exists(local_tar_path):
                # Compare the versions of the local tar file and the tar file on GitHub
                if compare_versions(local_tar_path, download_url):
                    # Versions are different, download the tar file
                    print(f"Downloading tar file: {download_url}")
                    wget = f"wget {download_url} -O {local_tar_path}"
                    os.system(wget)
                else:
                    print("Local tar file is up to date.")
            else:
                # Local tar file does not exist, download the tar file
                rm_tar = f"rm -rf lib/ bin/ iree*.tar.xz compiler-explorer/"
                os.system(rm_tar)
                print(f"Downloading tar file: {download_url}")
                wget = f"wget {download_url} -O {local_tar_path}"
                os.system(wget)
                untar = f"tar -xvf {local_tar_path}"
                os.system(untar)
            break

# Function to compare the versions of the local tar file and the tar file on GitHub
def compare_versions(local_tar_path, download_url):
    # Extract the version from the local tar file name
    local_version = extract_version(local_tar_path)

    # Extract the version from the GitHub tar file URL
    github_version = extract_version_from_url(download_url)

    # Compare the versions
    if local_version != github_version:
        return True
    else:
        return False

# Function to extract the version from the tar file name
def extract_version(file_path):
    file_name = os.path.basename(file_path)
    version = file_name.split("-")[2]
    return version

# Function to extract the version from the tar file URL
def extract_version_from_url(url):
    file_name = url.split("/")[-1]
    version = file_name.split("-")[2]
    return version

# Function to get the stored version
def get_stored_version():
    if os.path.exists(local_tar_path):
        return extract_version(local_tar_path)
    else:
        return None

# Function to update the stored version
def update_stored_version(version):
    if os.path.exists(local_tar_path):
        # Extract the directory path of the local tar file
        directory_path = os.path.dirname(local_tar_path)

        # Create the updated file name with the new version
        new_file_name = f"iree-dist-{version}-linux-x86_64.tar.xz"

        # Build the path for the updated file
        new_file_path = os.path.join(directory_path, new_file_name)

        # Rename the local tar file with the updated version
        os.rename(local_tar_path, new_file_path)

        # Update the local_tar_path variable with the new file path
        local_tar_path = new_file_path
    else:
        print("Local tar file does not exist. Update aborted.")

import os

# Function to download Compiler Explorer source code
def get_compiler_explorer():
    repo_url = "https://github.com/compiler-explorer/compiler-explorer.git"
    destination_path = "/home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/compiler-explorer"

    # Check if the destination folder already exists
    if os.path.exists(destination_path):
        print("Destination folder already exists.")
        return

    # Clone the repository using git
    clone_command = f"git clone {repo_url} {destination_path}"
    os.system(clone_command)

    print("Compiler Explorer source code downloaded successfully.")

def change_compiler_explorer_with_iree_compiler(path):
    # Specify the file path
    file_path = "compiler-explorer/etc/config/mlir.defaults.properties"
    # Specify the line to be replaced
    old_line = "compiler.mliropt14.exe=/usr/bin/mlir-opt-14"
    # Specify the new line
    new_line = f"compiler.mliropt14.exe={path}"

    # Read the contents of the file
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Replace the old line with the new line
    with open(file_path, "w") as f:
        for line in lines:
            if line.strip() == old_line:
                f.write(new_line + "\n")
            else:
                f.write(line)

def make_compiler_explorer():
  #os.system(" cd compiler-explorer")
  os.system("cd compiler-explorer && wget https://nodejs.org/dist/v18.16.0/node-v18.16.0-linux-x64.tar.xz && tar -xvf node-*.tar.xz")
  node_path="/home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/compiler-explorer/node-v18.16.0-linux-x64"
  make_cmd = "cd compiler-explorer && make NODE_DIR=" + node_path
  print (make_cmd)
  os.system(make_cmd)

# Run the check for new releases
check_new_pre_release()
get_compiler_explorer()
change_compiler_explorer_with_iree_compiler("/home/sameeran/workspace/SANDBOX/compiler_explorer_cron_iree/bin/")
make_compiler_explorer()


