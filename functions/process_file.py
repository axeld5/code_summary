import os
import json
from .genai_summary import generate_summary

EXCLUDED_EXTENSIONS = {'.yaml', '.yml', '.xlsx', '.docx', '.pptx', '.json', '.csv', '.png', '.jpeg', '.txt'}

def split_text_into_chunks(words, chunk_size=3000, context=1000):
    """
    Split a list of words into chunks of size 'chunk_size'.
    Each chunk will be extended by a context window of 'context' words before and after (if available).
    Returns a list of word lists (chunks).
    """
    chunks = []
    n = len(words)
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        context_start = max(0, start - context)
        context_end = min(n, end + context)
        chunks.append(words[context_start:context_end])
        start += chunk_size
    return chunks

# -----------------------------
# File Reader with IPYNB Processing
# -----------------------------
def read_file_content(file_path):
    """
    Read the file content. If the file is a Jupyter Notebook (.ipynb),
    extract and return only the cell sources for code and markdown cells.
    Otherwise, return the raw content.
    """
    _, ext = os.path.splitext(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return f"<Error reading file: {e}>"
    
    if ext.lower() == '.ipynb':
        try:
            nb = json.loads(content)
            cells = nb.get('cells', [])
            filtered_cells = []
            for cell in cells:
                cell_type = cell.get('cell_type', '')
                if cell_type in ('code', 'markdown'):
                    cell_source = ''.join(cell.get('source', []))
                    if cell_type == 'code':
                        filtered_cells.append(f"```python\n{cell_source}\n```\n")
                    elif cell_type == 'markdown':
                        filtered_cells.append(cell_source + "\n")
            content = "\n".join(filtered_cells)
        except Exception as e:
            content = f"<Error processing ipynb file: {e}>"
    return content

def process_file(file_path):
    """
    Read the file at 'file_path' and return a summary.
    If the file has more than 20k words, split it into overlapping chunks,
    summarize each, and aggregate the chunk summaries.
    If the file's extension is in EXCLUDED_EXTENSIONS, return a placeholder summary.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() in EXCLUDED_EXTENSIONS:
        return (f"<File '{os.path.basename(file_path)}' with extension '{ext}' "
                "is excluded from content summarization; only file name is included.>")
    
    content = read_file_content(file_path)
    words = content.split()
    if len(words) > 20000:
        chunks = split_text_into_chunks(words, chunk_size=4000, context=100)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            chunk_text = " ".join(chunk)
            summary = generate_summary(chunk_text)
            chunk_summaries.append(f"Chunk {i+1} summary: {summary}")
        return "\n".join(chunk_summaries)
    else:
        return generate_summary(content)