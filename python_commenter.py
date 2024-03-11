import ast
import logging
import datetime
import os
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Function to call the local LLM client
def call_local_llm(prompt, model="local-model", temperature=0.7):
    logging.debug(f"Calling local LLM with prompt: {prompt}")
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    response = completion.choices[0].message.content
    logging.debug(f"Local LLM response: {response}")
    return response

# Function to generate docstrings
def generate_docstring(node, node_type, context):
    logging.debug(f"Generating docstring for {node_type}")
    prompt = f"Generate a docstring for the following {node_type}:\n\n{context}"
    docstring = call_local_llm(prompt)
    node.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{docstring}"""')))

# Function to generate line comments
def generate_line_comment(node, context):
    logging.debug("Generating line comment")
    prompt = f"Generate a one-line comment explaining the following code:\n\n{context}"
    line_comment = call_local_llm(prompt)
    node.lineno = ast.Constant(value=f"# {line_comment}")

# Function to summarize the code
def summarize_code(script_ast, comments):
    logging.debug("Generating code summary")
    prompt = f"Summarize the following code and the added comments:\n\n{comments}"
    summary = call_local_llm(prompt)
    script_ast.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{summary}"""')))

# Helper function to get the source code context for a node
# Helper function to get the source code context for a node
def get_source_context(node, script_content):
    if isinstance(node, ast.Module):
        # For the root Module node, return the entire script content
        return script_content

    if isinstance(node, ast.Expr):
        # For Expr nodes, we can't use line numbers directly
        # Instead, we'll look for the next node with a line number
        next_node = next((n for n in ast.walk(node) if hasattr(n, 'lineno')), None)
        if next_node:
            start = next_node.lineno - 1
            end = start + 1  # Expr nodes are usually single-line
        else:
            return ""
    else:
        start = node.lineno - 1
        end = node.end_lineno

    source_lines = script_content.split("\n")[start:end]
    context = "\n".join(source_lines)
    return context

# Function to remove existing comments from the AST
def remove_existing_comments(script_ast):
    """
    Removes all existing comments (docstrings and line comments) from the AST.
    """
    logging.debug("Removing existing comments from the AST")
    for node in ast.walk(script_ast):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            # Remove docstrings
            if node.value.value.startswith('"""'):
                script_ast.body.remove(node)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith('#'):
            # Remove line comments
            node.value = ''

    return script_ast

# Function to modify the AST with docstrings, line comments, and summary
def modify_ast(script_ast, script_content, remove_existing_comments):
    logging.debug("Modifying AST with docstrings, line comments, and summary")

    if remove_existing_comments:
        # Remove existing comments
        script_ast = remove_existing_comments(script_ast)

    # Step 3: Generate Docstrings for Classes and Functions
    for node in script_ast.body:
        if isinstance(node, ast.ClassDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, "class", context)
        elif isinstance(node, ast.FunctionDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, "function", context)

    # Step 4: Generate Line Comments
    for node in ast.walk(script_ast):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            context = get_source_context(node, script_content)
            generate_line_comment(node, context)
        elif not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Expr, ast.Constant)) and not is_empty_line(node):
            context = get_source_context(node, script_content)
            generate_line_comment(node, context)

    # Step 5: Summarize the Code
    comments = ast.dump(script_ast, indent=4)
    summarize_code(script_ast, comments)

    return script_ast

# Helper function to check if a line is empty
def is_empty_line(node):
    source_code = ast.unparse(node).strip()
    return not source_code

# Step 1 (from previous outline)
def load_and_parse_script(file_path):
    logging.debug(f"Loading and parsing script: {file_path}")
    try:
        with open(file_path, 'r') as file:
            script_content = file.read()
    except FileNotFoundError:
        logging.error(f"Error: File '{file_path}' not found.")
        return None, None

    try:
        script_ast = ast.parse(script_content)
    except SyntaxError as e:
        logging.error(f"Error: Syntax error in the script: {e}")
        return None, None

    return script_ast, script_content

# Function to generate the updated script from the modified AST
def generate_updated_script(script_ast):
    updated_script = ast.unparse(script_ast)
    return updated_script

# Function to save the updated script to a file
def save_updated_script(updated_script, original_file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name, file_ext = os.path.splitext(os.path.basename(original_file_path))
    new_file_name = f"{file_name}_{timestamp}{file_ext}"
    new_file_path = os.path.join(os.path.dirname(original_file_path), new_file_name)

    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_script)

    logging.info(f"Updated script saved to: {new_file_path}")

# Example usage
if __name__ == "__main__":
    script_path = "test_script.py"
    logging.debug(f"Processing script: {script_path}")
    script_ast, script_content = load_and_parse_script(script_path)
    if script_ast:
        remove_existing_comments = input("Do you want to remove existing comments? (y/n) ").lower() == "y"
        modified_ast = modify_ast(script_ast, script_content, remove_existing_comments)
        updated_script = generate_updated_script(modified_ast)
        save_updated_script(updated_script, script_path)
    else:
        logging.error("Failed to process the script.")