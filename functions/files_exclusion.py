import os
import pathspec

# -----------------------------
# Exclusion Rules and Settings
# -----------------------------
EXCLUDED_DIRS = {'.git', '.svn', '__pycache__', 'pycache'}
EXCLUDED_FILES = {'.env'}
# Additional forbidden extensions – note these files will be included by name only.
EXCLUDED_EXTENSIONS = {
    '.yaml', 
    '.yml', 
    '.xlsx', 
    '.docx', 
    '.pptx', 
    '.json', 
    '.csv', 
    '.png', 
    '.jpeg', 
    '.txt', 
    '.wav', 
    '.mp3', 
    '.mp4', 
    '.lock', 
    '.ptl',
    '.h5',
    '.pdf',
    '.pickle'
}

# Mapping file extensions to language tags for code blocks.
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

def should_exclude_dir(dir_name):
    """Return True if the directory should be excluded (hidden or in EXCLUDED_DIRS)."""
    return dir_name.startswith('.') or dir_name in EXCLUDED_DIRS

def should_exclude_file(file_name):
    """
    Return True if the file should be fully excluded from the tree.
    We still exclude hidden files or those explicitly listed (e.g. '.env').
    Files with forbidden extensions are *not* excluded—they will be included by name.
    """
    if file_name.startswith('.'):
        return True
    if file_name in EXCLUDED_FILES:
        return True
    return False

def should_process_file_content(file_name):
    """
    Return True if the file's content should be read and processed.
    Files with extensions in EXCLUDED_EXTENSIONS are not processed (only the file name is included).
    """
    _, ext = os.path.splitext(file_name)
    return ext.lower() not in EXCLUDED_EXTENSIONS

def load_gitignore(repo_root):
    """
    Load and compile .gitignore patterns from the repository root.
    Returns a pathspec.PathSpec object or None if no .gitignore is found.
    """
    gitignore_path = os.path.join(repo_root, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            patterns = f.read().splitlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    return None

def should_exclude_by_gitignore(relative_path, gitignore_spec):
    """
    Return True if the file/folder (given by its path relative to the repo root)
    matches a pattern from .gitignore.
    """
    if gitignore_spec is None:
        return False
    posix_path = relative_path.replace(os.sep, '/')
    return gitignore_spec.match_file(posix_path)