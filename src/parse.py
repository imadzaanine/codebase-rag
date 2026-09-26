import os 
from tree_sitter_languages import get_parser

# Map file extensions to tree-sitter language names
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".rb": "ruby",
}

# Which tree-sitter node types count as a "chunk" (function/class/method) per language
CHUNK_NODE_TYPES = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "method_definition"},
    "typescript": {"function_declaration", "class_declaration", "method_definition"},
    "java": {"method_declaration", "class_declaration"},
    "go": {"function_declaration", "method_declaration"},
    "rust": {"function_item", "impl_item"},
    "c": {"function_definition"},
    "cpp": {"function_definition", "class_specifier"},
    "ruby": {"method", "class"},
}

SKIP_DIRS = {".git", "venv", ".venv", "__pycache__", "node_modules", "dist", "build", "target"}


def find_source_files(repo_path):
    """Walk a repo and return paths to all files with a recognized extension."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in filenames:
            ext = os.path.splitext(filename)[1]
            if ext in EXTENSION_TO_LANGUAGE:
                files.append(os.path.join(root, filename))
    return files



def extract_chunks_from_file(file_path):

    ext = os.path.splitext(file_path)[1]
    language = EXTENSION_TO_LANGUAGE.get(ext)
    if language is None:
        return[]

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source_code = f.read()

    parser = get_parser(language)
    tree = parser.parse(bytes(source_code, "utf-8"))
    
    target_node_types = CHUNK_NODE_TYPES.get(language, set())
    chunks = []
    
    def walk(node):
        if node.type in target_node_types:
            code_segment = source_code[node.start_byte:node.end_byte]
            chunks.append({
                "code": code_segment,
                "type": node.type,
                "language": language,
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,  # tree-sitter is 0-indexed
            })
        for child in node.children:
            walk(child)
    
    walk(tree.root_node)
    return chunks

def parse_repo(repo_path):
    """Extract all function/class chunks from every recognized source file in a repo."""
    source_files = find_source_files(repo_path)
    print(f"Found {len(source_files)} source files across recognized languages.")
    
    all_chunks = []
    for file_path in source_files:
        try:
            chunks = extract_chunks_from_file(file_path)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Skipping {file_path}: {e}")
    
    print(f"Extracted {len(all_chunks)} functions/classes total.")
    return all_chunks


if __name__ == "__main__":
    from clone import clone_repo
    
    repo_url = input("Enter a GitHub repo URL: ")
    repo_path = clone_repo(repo_url)
    
    chunks = parse_repo(repo_path)
    
    if chunks:
        print("\n--- Sample chunk ---")
        print("Type:", chunks[0]["type"])
        print("Language:", chunks[0]["language"])
        print("File:", chunks[0]["file_path"])
        print("Line:", chunks[0]["start_line"])
        print("Code:\n", chunks[0]["code"])





