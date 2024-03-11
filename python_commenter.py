import ast
import logging
import datetime
import os
from openai import OpenAI

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

def call_local_llm(prompt, model="local-model", temperature=0.7):
    try:
        logging.debug(f"Calling local LLM with prompt: {prompt}")
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        response = completion.choices[0].message.content
        logging.debug(f"Local LLM response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error calling local LLM: {e}")
        return ""

def generate_docstring(node, node_type, context):
    try:
        logging.debug(f"Generating docstring for {node_type}")
        prompt = f"Generate a docstring for the following {node_type}:\n\n{context}"
        docstring = call_local_llm(prompt)
        node.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{docstring}"""')))
    except Exception as e:
        logging.error(f"Error generating docstring: {e}")

def generate_line_comment(node, context):
    logging.debug("Generating line comment")
    prompt = f"Generate a one-line comment explaining the following code:\n\n{context}"
    line_comment = call_local_llm(prompt)
    node.lineno = ast.Constant(value=f"# {line_comment}")

def summarize_code(script_ast, comments):
    logging.debug("Generating code summary")
    prompt = f"Summarize the following code and the added comments:\n\n{comments}"
    summary = call_local_llm(prompt)
    script_ast.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{summary}"""')))

def get_source_context(node, script_content):
    if hasattr(node, 'lineno'):
        start = node.lineno - 1
        end = node.end_lineno
    else:
        start = None
        end = None

    if isinstance(node, ast.Module):
        return script_content
    elif isinstance(node, ast.Expr):
        next_node = next((n for n in ast.walk(node) if hasattr(n, 'lineno')), None)
        if next_node:
            start = next_node.lineno - 1
            end = start + 1
        else:
            return ""

    if start is not None and end is not None:
        source_lines = script_content.splitlines()[start:end]
        context = "\n".join(source_lines)
        return context
    else:
        return ""

def should_comment_line(node):
    if isinstance(node, (ast.Assign, ast.If, ast.For)):
        return True
    else:
        return False

def insert_line_comment(node, comment):
    ast.insert_before(node, ast.parse("# " + comment).body[0])

def remove_existing_comments(script_ast):
    try:
        logging.debug("Removing existing comments from the AST")

        def remove_comments(node):
            if isinstance(node, ast.Module):
                node.body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant) or not n.value.value.startswith('"""')]
                for child in node.body:
                    remove_comments(child)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                node.body = [n for n in node.body if not isinstance(n, ast.Constant) or not isinstance(n.value, str) or not n.value.startswith('#')]
                for child in node.body:
                    remove_comments(child)

        remove_comments(script_ast)

    except Exception as e:
        logging.error(f"Error removing existing comments: {e}")

    return script_ast

def modify_ast(script_ast, script_content):
    logging.debug("Modifying AST with docstrings, line comments, and summary")

    for node in script_ast.body:
        if isinstance(node, ast.ClassDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, "class", context)
        elif isinstance(node, ast.FunctionDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, "function", context)

    for node in ast.walk(script_ast):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            continue

        context = get_source_context(node, script_content)

        if context:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                comment = generate_line_comment(node, context)
            elif should_comment_line(node):
                comment = generate_line_comment(node, context)
            else:
                comment = ""

            if comment:
                insert_line_comment(node, comment)

    comments = ast.dump(script_ast, indent=4)
    summarize_code(script_ast, comments)

    return script_ast

def is_empty_line(node):
    source_code = ast.unparse(node).strip()
    return not source_code

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

def generate_updated_script(script_ast):
    updated_script = ast.unparse(script_ast)
    return updated_script

def save_updated_script(updated_script, original_file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name, file_ext = os.path.splitext(os.path.basename(original_file_path))
    new_file_name = f"{file_name}_{timestamp}{file_ext}"
    new_file_path = os.path.join(os.path.dirname(original_file_path), new_file_name)

    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_script)

    logging.info(f"Updated script saved to: {new_file_path}")

if __name__ == "__main__":
    script_path = "python_commenter.py"
    script_ast, script_content = load_and_parse_script(script_path)
    if script_ast:
        remove_existing_comments = input("Do you want to remove existing comments? (y/n) ").lower() == "y"
        
        # Check if remove_existing_comments is a boolean value
        print(f"Type of remove_existing_comments: {type(remove_existing_comments)}")
        
        if remove_existing_comments:
            # Check the type of script_ast before passing it to remove_existing_comments
            print(f"Type of script_ast before remove_existing_comments: {type(script_ast)}")
            
            script_ast = remove_existing_comments(script_ast)
            
            # Check the type of script_ast after remove_existing_comments
            print(f"Type of script_ast after remove_existing_comments: {type(script_ast)}")
        
        modified_ast = modify_ast(script_ast, script_content)
        updated_script = generate_updated_script(modified_ast)
        save_updated_script(updated_script, script_path)
    else:
        logging.error("Failed to process the script.")