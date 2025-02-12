import os

from .files_exclusion import should_process_file_content, should_exclude_by_gitignore, should_exclude_file, should_exclude_dir, EXCLUDED_DIRS

class FolderNode:
    def __init__(self, name, path):
        self.name = name          # Folder name
        self.path = path          # Full folder path
        self.files = []           # List of file names in this folder
        self.subfolders = []      # List of child FolderNode objects
        self.summary = None       # Final summary text for the folder

    def add_subfolder(self, subfolder):
        self.subfolders.append(subfolder)

    def add_file(self, file_name):
        self.files.append(file_name)

    def __repr__(self):
        return f"<FolderNode name={self.name} files={len(self.files)} subfolders={len(self.subfolders)}>"

def build_folder_tree(path, repo_root, gitignore_spec):
    """
    Recursively build a tree of FolderNode objects starting at 'path',
    applying all exclusion rules (hidden files/folders, forbidden names, and .gitignore).
    """
    node = FolderNode(name=os.path.basename(path) or path, path=path)
    try:
        with os.scandir(path) as it:
            for entry in it:
                rel_path = os.path.relpath(entry.path, repo_root)
                if should_exclude_by_gitignore(rel_path, gitignore_spec):
                    continue

                if entry.is_dir(follow_symlinks=False):
                    if should_exclude_dir(entry.name):
                        continue
                    child = build_folder_tree(entry.path, repo_root, gitignore_spec)
                    node.add_subfolder(child)
                elif entry.is_file(follow_symlinks=False):
                    # Exclude the analysis script itself.
                    if should_exclude_file(entry.name):
                        continue
                    node.add_file(entry.name)
    except PermissionError:
        print(f"Permission denied: {path}")
    return node

# -----------------------------
# Utility: Flatten the Summary Tree
# -----------------------------
def flatten_tree(node, prefix=""):
    """
    Recursively flatten the folder tree into a dict mapping hierarchical names to summaries.
    """
    if prefix:
        full_name = prefix + " > " + node.name
    else:
        full_name = node.name
    results = {full_name: node.summary}
    for child in node.subfolders:
        results.update(flatten_tree(child, prefix=full_name))
    return results