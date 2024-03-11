'''""""""'''
import ast
import logging
import datetime
import os
from openai import OpenAI
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
client = OpenAI(base_url='http://localhost:1234/v1', api_key='not-needed')

def call_local_llm(prompt, model='local-model', temperature=0.7):
    '''""" """
Call the local LLM using provided prompt, model, and temperature. If successful, return the generated response from the local LLM. If an error occurs during the call, log the error and return an empty string.

Parameters:
- prompt (str): The input text to be used as a prompt for the local LLM.
- model (str): The name of the model to be used for generating responses. Default is "local-model".
- temperature (float): A floating point value between 0 and 1 that controls the randomness of the generated response. Default is 0.7.

Returns:
- str: The textual response generated by the local LLM if successful, otherwise an empty string.
""""""'''
    try:
        logging.debug(f'Calling local LLM with prompt: {prompt}')
        completion = client.chat.completions.create(model=model, messages=[{'role': 'user', 'content': prompt}], temperature=temperature)
        response = completion.choices[0].message.content
        logging.debug(f'Local LLM response: {response}')
        return response
    except Exception as e:
        logging.error(f'Error calling local LLM: {e}')
        return ''

def generate_docstring(node, node_type, context):
    '''""" """
Generate a docstring for the given node of type `node_type` in the context provided by `context`.

Args:
- node (ast.Node): The AST node for which the docstring is being generated.
- node_type (str): The type of the AST node, e.g., 'Function', 'Class'.
- context (str): The context in which the AST node exists, used to help generate an appropriate docstring.

Returns:
- str: The generated docstring for the given `node` and `context`.

Raises:
- Exception: If an error occurs while generating the docstring.

Example:

```python
import ast

def example_function():
    pass

example_ast = ast.parse("example_function()")
generate_docstring(example_ast, "Function", "This is a function that does something.")
```""""""'''
    try:
        logging.debug(f'Generating docstring for {node_type}')
        prompt = f'Generate a docstring for the following {node_type}:\n\n{context}'
        docstring = call_local_llm(prompt)
        node.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{docstring}"""')))
    except Exception as e:
        logging.error(f'Error generating docstring: {e}')

def generate_line_comment(node, context):
    '''""" """
This function generates a one-line comment to explain the given code context. It uses an external Language Model (LLM) to generate the comment, and then adds it as a line comment above the original node in the abstract syntax tree (AST).

Parameters:
    - node (ast.Node): The AST node for which the comment will be generated.
    - context (str): The code context that will be provided to the Language Model to generate the comment.

Returns:
    - None: The function modifies the given node's lineno attribute by adding a one-line comment above it.
""""""'''
    logging.debug('Generating line comment')
    prompt = f'Generate a one-line comment explaining the following code:\n\n{context}'
    line_comment = call_local_llm(prompt)
    node.lineno = ast.Constant(value=f'# {line_comment}')

def summarize_code(script_ast, comments):
    '''""" def summarize_code(script_ast, comments):
    """
    This function takes a Python script AST (Abstract Syntax Tree) and a list of comments as input. It uses an LLM (Language Model) to generate a summary of the code along with the added comments. The generated summary is then inserted at the beginning of the script AST using the given comments as a prompt for the LLM.

    :param script_ast: The Abstract Syntax Tree representing the Python script.
    :type script_ast: ast.Module
    :param comments: List of comments to be included in the summary.
    :type comments: list of strings
    :returns: None
    """"""'''
    logging.debug('Generating code summary')
    prompt = f'Summarize the following code and the added comments:\n\n{comments}'
    summary = call_local_llm(prompt)
    script_ast.body.insert(0, ast.Expr(value=ast.Constant(value=f'"""{summary}"""')))

def get_source_context(node, script_content):
    '''""" """
get_source_context(node, script_content)
-------------------------------------
Return the source context of a given node in a script.

Parameters:
- node (ast.AST): The Python abstract syntax tree (AST) node for which to retrieve the context.
- script_content (str): The content of the script containing the AST node.

Returns:
- str: The source code context around the given AST node, or an empty string if it cannot be determined.

Examples:
>>> get_source_context(ast.Module(), "def func():\\n    pass\\n")
"def func():\\n    pass\\n"
>>> get_source_context(ast.Name(id='func'), "def func():\\n    pass\\n")
"def func():\\n    pass\\n"
>>> get_source_context(ast.Name(id='func'), "def main():\\ndef func():\\n    pass\\n")
"\\ndef main():\\ndef func():\\n    pass\\n"
""""""'''
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
            return ''
    if start is not None and end is not None:
        source_lines = script_content.splitlines()[start:end]
        context = '\n'.join(source_lines)
        return context
    else:
        return ''

def should_comment_line(node):
    '''""" """
This function checks whether a given Python abstract syntax tree node represents a line of code that should be commented or not. If the node is an assignment statement, an if statement, or a for loop, the function returns `True`, indicating that it should be commented. Otherwise, it returns `False`.

:param node: The Python abstract syntax tree node to be checked.
:type node: ast.AST or subclass thereof
:return: `True` if the line of code represented by the node should be commented; otherwise `False`.
:rtype: bool
""""""'''
    if isinstance(node, (ast.Assign, ast.If, ast.For)):
        return True
    else:
        return False

def insert_line_comment(node, comment):
    '''""" """
Insert a line comment before a given AST node with the specified comment text.

Parameters:
- node (ast.AST): The Python abstract syntax tree node where the comment should be inserted.
- comment (str): The text of the comment to be added.

Returns:
- None

Example usage:
```python
# Create an example AST node and a line comment
node = ast.Name(id='example')
comment = 'This is an example comment'

# Insert the line comment before the given node
insert_line_comment(node, comment)
```
""""""'''
    ast.insert_before(node, ast.parse('# ' + comment).body[0])

def remove_existing_comments(script_ast):
    '''""" """
Removes all existing comments from a Python AST (Abstract Syntax Tree). This function recursively checks each node in the AST and removes any comment nodes it finds.

Parameters:
- `script_ast` (ast.Module): The root of the Abstract Syntax Tree to modify.

Returns:
- `ast.Module`: The modified AST with all existing comments removed.
""""""'''
    try:
        logging.debug('Removing existing comments from the AST')

        def remove_comments(node):
            if isinstance(node, ast.Module):
                node.body = [n for n in node.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant) or (not n.value.value.startswith('"""'))]
                for child in node.body:
                    remove_comments(child)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                node.body = [n for n in node.body if not isinstance(n, ast.Constant) or not isinstance(n.value, str) or (not n.value.startswith('#'))]
                for child in node.body:
                    remove_comments(child)
        remove_comments(script_ast)
    except Exception as e:
        logging.error(f'Error removing existing comments: {e}')
    return script_ast

def modify_ast(script_ast, script_content):
    '''""" def modify_ast(script_ast, script_content):
    """
    Modifies the Abstract Syntax Tree (AST) with docstrings, line comments, and summary.
    
    Args:
        script_ast (ast): The Abstract Syntax Tree of the Python script.
        script_content (str): The content of the Python script.
    
    Returns:
        ast: The modified Abstract Syntax Tree with docstrings, line comments, and summary.
        
    """
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

    return script_ast"""'''
    logging.debug('Modifying AST with docstrings, line comments, and summary')
    for node in script_ast.body:
        if isinstance(node, ast.ClassDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, 'class', context)
        elif isinstance(node, ast.FunctionDef):
            context = get_source_context(node, script_content)
            generate_docstring(node, 'function', context)
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
                comment = ''
            if comment:
                insert_line_comment(node, comment)
    comments = ast.dump(script_ast, indent=4)
    summarize_code(script_ast, comments)
    return script_ast

def is_empty_line(node):
    '''""" """
This function takes an abstract syntax tree (AST) node and checks if it represents an empty line in the Python source code. It does this by first unparsing the AST node into its corresponding source code representation, then stripping any leading or trailing whitespace from the result. Finally, the function returns True if the resulting source code is empty, indicating an empty line; otherwise, False is returned.
""""""'''
    source_code = ast.unparse(node).strip()
    return not source_code

def load_and_parse_script(file_path):
    '''""" """
This function loads and parses a Python script from the given file path. It uses the built-in 'ast' module to parse the script into abstract syntax trees (AST). If the file is not found or there is a syntax error in the script, it logs an error message and returns None for both AST and script content.

Parameters:
    file_path (str): The path of the Python script to be loaded and parsed.

Returns:
    ast.Module: The abstract syntax tree (AST) representation of the script, or None if there was an error.
    str: The content of the script, or None if there was an error.
""""""'''
    logging.debug(f'Loading and parsing script: {file_path}')
    try:
        with open(file_path, 'r') as file:
            script_content = file.read()
    except FileNotFoundError:
        logging.error(f"Error: File '{file_path}' not found.")
        return (None, None)
    try:
        script_ast = ast.parse(script_content)
    except SyntaxError as e:
        logging.error(f'Error: Syntax error in the script: {e}')
        return (None, None)
    return (script_ast, script_content)

def generate_updated_script(script_ast):
    '''""" """
generate_updated_script(script_ast)
------------------------
This function takes a script abstract syntax tree (AST) as input and returns the updated script as a string. It uses the `ast.unparse` module to convert the AST back into its original source code representation, effectively updating the script with any changes made in the AST.

Parameters:
- script_ast (ast.Module): The abstract syntax tree of the script to be updated.

Returns:
- str: The updated script as a string.
""""""'''
    updated_script = ast.unparse(script_ast)
    return updated_script

def save_updated_script(updated_script, original_file_path):
    '''""" """
save_updated_script function takes an updated script and the path of the original script, saves the updated script with a timestamp in its name, and logs the new file path.

Arguments:
- updated_script (str): The content of the updated script.
- original_file_path (str): The path of the original script.

Returns:
None. Saves the updated script to a new file with a timestamp and logs the new file path.
""""""'''
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name, file_ext = os.path.splitext(os.path.basename(original_file_path))
    new_file_name = f'{file_name}_{timestamp}{file_ext}'
    new_file_path = os.path.join(os.path.dirname(original_file_path), new_file_name)
    with open(new_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_script)
    logging.info(f'Updated script saved to: {new_file_path}')
if __name__ == '__main__':
    script_path = 'python_commenter.py'
    script_ast, script_content = load_and_parse_script(script_path)
    if script_ast:
        remove_existing_comments = input('Do you want to remove existing comments? (y/n) ').lower() == 'y'
        print(f'Type of remove_existing_comments: {type(remove_existing_comments)}')
        if remove_existing_comments:
            print(f'Type of script_ast before remove_existing_comments: {type(script_ast)}')
            script_ast = remove_existing_comments(script_ast)
            print(f'Type of script_ast after remove_existing_comments: {type(script_ast)}')
        modified_ast = modify_ast(script_ast, script_content)
        updated_script = generate_updated_script(modified_ast)
        save_updated_script(updated_script, script_path)
    else:
        logging.error('Failed to process the script.')