import os
import json
import subprocess
import tempfile
import shutil
import datetime

from functions.folder_tree import FolderNode, build_folder_tree, flatten_tree
from functions.files_exclusion import load_gitignore
from functions.folder_summarization import summarize_folder

# Folder where summary tree structures will be saved.
EXAMPLE_REPOS_DIR = "../example_repos"
if not os.path.exists(EXAMPLE_REPOS_DIR):
    os.makedirs(EXAMPLE_REPOS_DIR)

# -----------------------------
# Utility: Extract Name from Repo/Folder
# -----------------------------
def get_repo_or_folder_name(path_or_url: str, mode: str) -> str:
    if mode == 'repo':
        # e.g., "https://github.com/username/repository.git"
        name = path_or_url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name
    else:
        return os.path.basename(os.path.abspath(path_or_url))

# -----------------------------
# Repository Summarization Functions
# -----------------------------
def summarize_repo(repo_url: str) -> (str, FolderNode):
    """
    Clone the repository from repo_url, build the folder tree, and generate the summary.
    Returns a tuple (global_summary_text, root_tree_node).
    """
    temp_dir = tempfile.mkdtemp(prefix="repo_")
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir)
        return f"Error cloning repository: {e}", None
    repo_root = temp_dir
    gitignore_spec = load_gitignore(repo_root)
    tree = build_folder_tree(repo_root, repo_root, gitignore_spec)
    global_summary = summarize_folder(tree)
    shutil.rmtree(temp_dir)
    return global_summary, tree

def run_repo_summary(repo_url: str) -> str:
    """
    Function intended for Gradio: it runs the summarization on a repo, saves the global summary and
    the flattened summary tree, and returns the global summary text along with file save locations.
    """
    repo_name = get_repo_or_folder_name(repo_url, 'repo')
    summary_text, tree = summarize_repo(repo_url)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(EXAMPLE_REPOS_DIR, f"{repo_name}_summary_{timestamp}.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_text)
    if tree is not None:
        flattened = flatten_tree(tree)
        tree_file = os.path.join(EXAMPLE_REPOS_DIR, f"{repo_name}_summary_tree_{timestamp}.json")
        with open(tree_file, "w", encoding="utf-8") as f:
            json.dump(flattened, f, indent=2)
        return (summary_text + 
                f"\n\nGlobal summary saved to: {summary_file}" +
                f"\nSummary tree saved to: {tree_file}")
    else:
        return summary_text