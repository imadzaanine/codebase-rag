import os 
import git 
from urllib.parse import urlparse


def clone_repo(repo_url, base_path = "repos"):

    repo_name = urlparse(repo_url).path.strip("/").split("/")[-1]
    repo_name = repo_name.replace(".git","")

    local_path = os.path.join(base_path, repo_name)

    if os.path.exists(local_path):
        print(f"Repo already cloned at {local_path}, skipping.")
        return local_path

    print(f"Cloning {repo_url} into {local_path}...")
    git.Repo.clone_from(repo_url, local_path)
    print("Done.")

    return local_path


if __name__ == "__main__":
    repo_url = input("Enter a GitHub repo URL: ")
    path = clone_repo(repo_url)
    print("Cloned to:", path)