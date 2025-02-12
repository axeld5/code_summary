import os

from .process_file import read_file_content, process_file
from .files_exclusion import should_process_file_content
from .genai_summary import generate_summary

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


def summarize_folder(node):
    """
    Recursively traverse the folder tree (bottom-up) and generate a summary.

    For each folder:
      1. Process subfolders first (their summaries are aggregated).
      2. Process the folder’s own files:
         - For files with allowed extensions, include their content (with appropriate code blocks).
         - For files with excluded extensions, include only the file name and a placeholder.
      3. If the aggregated text is huge (over 20k words), process each file using process_file.
      4. Compute the final text’s word count and store it in the folder summary.

    The function returns the final aggregated text for the folder.
    """
    # Process subfolders recursively.
    aggregated_subfolder_text = ""
    for subfolder in node.subfolders:
        sub_text = summarize_folder(subfolder)
        aggregated_subfolder_text += f"\n### Subfolder '{subfolder.name}' ---\n{sub_text}\n"

    # Process current folder's own files.
    raw_file_texts = []
    for file_name in node.files:
        file_path = os.path.join(node.path, file_name)
        _, ext = os.path.splitext(file_name)
        header = f"--- {file_name} ---\n"
        if should_process_file_content(file_name):
            content = read_file_content(file_path)
            language_tag = LANGUAGE_TAGS.get(ext.lower(), '')
            if language_tag:
                block = f"```{language_tag}\n{content}\n```\n"
            else:
                block = f"```\n{content}\n```\n"
        else:
            block = (f"<File '{file_name}' with extension '{ext}' is excluded from processing; "
                     "only file name is included>\n")
        raw_file_texts.append(header + block)
    combined_raw_text = "\n".join(raw_file_texts) + "\n" + aggregated_subfolder_text
    total_words = len(combined_raw_text.split())
    # If the folder's aggregated text is huge, summarize each file separately.
    if total_words > 20000:
        summarized_file_texts = []
        for file_name in node.files:
            file_path = os.path.join(node.path, file_name)
            _, ext = os.path.splitext(file_name)
            if should_process_file_content(file_name):
                summarized = process_file(file_path)
            else:
                summarized = (f"<File '{file_name}' with extension '{ext}' is excluded from content summarization; "
                              "only file name is included.>")
            summarized_file_texts.append(f"--- {file_name} ---\n{summarized}\n")
        full_text_summary = generate_summary("\n".join(summarized_file_texts))
    else:
        full_text_summary = generate_summary(combined_raw_text)

    node.summary = (
        f"Folder '{node.name}' summary:\n"
        f"{full_text_summary}"
    )
    print(node.summary)
    return full_text_summary