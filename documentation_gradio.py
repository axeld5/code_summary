import json
import os
import sys
import gradio as gr

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
# Functions for Loading Saved Summaries (Global Text)
# -----------------------------

EXAMPLE_REPOS_DIR = "example_repos"
if not os.path.exists(EXAMPLE_REPOS_DIR):
    os.makedirs(EXAMPLE_REPOS_DIR)
    
def list_saved_summaries() -> list:
    files = [f for f in os.listdir(EXAMPLE_REPOS_DIR) if f.endswith('.txt')]
    return sorted(files, reverse=True)

def load_structure(file_name: str) -> str:
    file_path = os.path.join(EXAMPLE_REPOS_DIR, file_name)
    if not os.path.exists(file_path):
        return f"File {file_name} not found."
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

# -----------------------------
# Functions for Loading Saved Summary Trees
# -----------------------------
def list_saved_trees() -> list:
    files = [f for f in os.listdir(EXAMPLE_REPOS_DIR) if f.startswith("summary_tree_") and f.endswith('.json')]
    return sorted(files, reverse=True)

def load_tree_file(file_name: str) -> (list, dict):
    """
    Load a saved summary tree JSON file.
    Returns a tuple: (list of hierarchical keys, the full flattened dict).
    """
    file_path = os.path.join(EXAMPLE_REPOS_DIR, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree_dict = json.load(f)
        keys = list(tree_dict.keys())
        return keys, tree_dict
    except Exception as e:
        return [], {}

def get_node_summary(node_key: str, tree_dict: dict) -> str:
    return tree_dict.get(node_key, "Summary not found.")

if "--gradio" in sys.argv:
    with gr.Blocks() as demo:
        gr.Markdown("## Repo Summarizer Interface")
        with gr.Tabs():
            with gr.Tab("Load Global Summary"):
                saved_files_dropdown = gr.Dropdown(label="Saved Global Summaries", choices=list_saved_summaries())
                load_button = gr.Button("Load Summary")
                loaded_summary_output = gr.Markdown()
                load_button.click(fn=load_structure, inputs=saved_files_dropdown, outputs=loaded_summary_output)
                refresh_button = gr.Button("Refresh List")
                refresh_button.click(fn=list_saved_summaries, inputs=[], outputs=saved_files_dropdown)
            with gr.Tab("View Summary Tree"):
                gr.Markdown("### Load a saved summary tree and inspect subsummaries")
                tree_files_dropdown = gr.Dropdown(label="Saved Summary Trees", choices=list_saved_trees())
                load_tree_button = gr.Button("Load Summary Tree")
                tree_state = gr.State({})
                node_dropdown = gr.Dropdown(label="Select Folder/Subfolder", choices=[])
                node_summary_output = gr.Markdown()
                def load_tree_fn(file_name: str):
                    keys, tree_dict = load_tree_file(file_name)
                    default = keys[0] if keys else None
                    return gr.update(choices=keys, value=default), tree_dict
                load_tree_button.click(fn=load_tree_fn, inputs=tree_files_dropdown, outputs=[node_dropdown, tree_state])
                node_dropdown.change(fn=lambda key, state: get_node_summary(key, state),
                                    inputs=[node_dropdown, tree_state],
                                    outputs=node_summary_output)
    demo.launch(share=True)