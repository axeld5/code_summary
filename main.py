import os
import json
import subprocess
import tempfile
import stat
import shutil
import argparse

from functions.folder_tree import FolderNode, build_folder_tree, flatten_tree
from functions.files_exclusion import load_gitignore
from functions.folder_summarization import summarize_folder
from functions.utils import get_repo_or_folder_name

def remove_readonly(func, path, _):
    """Change the file permission and retry deletion."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

LANGUAGE_TAGS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.html': 'html',
    '.css': 'css',
    '.sh': 'bash',
}

EXAMPLE_REPOS_DIR = "example_repos"
if not os.path.exists(EXAMPLE_REPOS_DIR):
    os.makedirs(EXAMPLE_REPOS_DIR)


# -----------------------------
# Command-Line Main Function
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Process and summarize a local folder or a GitHub repository."
    )
    parser.add_argument(
        '--path_or_url',
        help="Path to the local folder (for local mode) or GitHub repo URL (for repo mode)."
    )
    parser.add_argument(
        '--mode',
        choices=['local', 'repo'],
        required=True,
        help="Mode of operation: 'local' for a folder, 'repo' to clone a GitHub repository."
    )
    args = parser.parse_args()

    if args.mode == 'local':
        repo_name = get_repo_or_folder_name(args.path_or_url, 'local')
        repo_root = os.path.abspath(args.path_or_url)
        if not os.path.exists(repo_root) or not os.path.isdir(repo_root):
            print(f"Local folder {repo_root} does not exist or is not a directory.")
            exit(1)
        gitignore_spec = load_gitignore(repo_root)
        tree = build_folder_tree(repo_root, repo_root, gitignore_spec)
        global_summary = summarize_folder(tree)
    else:
        repo_name = get_repo_or_folder_name(args.path_or_url, 'repo')
        temp_dir = os.path.join(tempfile.gettempdir(), repo_name)
        print(f"Cloning repository {args.path_or_url} into {temp_dir}")
        try:
            subprocess.run(["git", "clone", args.path_or_url, temp_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            shutil.rmtree(temp_dir, onerror=remove_readonly)
            exit(1)
        repo_root = temp_dir
        gitignore_spec = load_gitignore(repo_root)
        tree = build_folder_tree(repo_root, repo_root, gitignore_spec)
        global_summary = summarize_folder(tree)
        shutil.rmtree(temp_dir, onerror=remove_readonly)
        print(f"Cleaned up temporary repository folder {temp_dir}")

    print("\n===== GLOBAL SUMMARY =====\n")
    print(global_summary)

    summary_file = os.path.join(EXAMPLE_REPOS_DIR, f"summary_{repo_name}.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(global_summary)
    print(f"\nGlobal summary saved to {summary_file}")

    # Also save the flattened summary tree (for subsummaries).
    flattened = flatten_tree(tree)
    tree_file = os.path.join(EXAMPLE_REPOS_DIR, f"summary_tree_{repo_name}.json")
    with open(tree_file, "w", encoding="utf-8") as f:
        json.dump(flattened, f, indent=2)
    print(f"Summary tree saved to {tree_file}")

if __name__ == "__main__":
    main()