import json
import ast
import astor
import ast_comments

def remove_comments(py_file):
    """Removes comments from a Python script using ast-comments.

    Args:
        py_file: The Python script as a string.

    Returns:
        The Python script without comments as a string.
    """
    tree = ast_comments.parse(py_file)
    new_lines = []
    for node in tree.body:
        if isinstance(node, ast_comments.Comment):
            continue  # Skip comment nodes
        new_lines.append(ast_comments.dump(node))  # Convert node to string without comments
    return ''.join(new_lines)


def parse_script(script_path):
    """Parses a Python script and returns information as JSON."""
    imports = []
    global_variables = {}
    functions = {}
    classes = {}
    current_scope = []  # Track the current scope

    with open(script_path, 'r') as file:
        source_code = file.read()

        # Remove comments from the source code
        cleaned_source = remove_comments(source_code)

        tree = ast.parse(cleaned_source, filename=script_path)

        # Traverse the AST to extract components
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.dump(node))
            elif isinstance(node, ast.Assign):
                # Check for top-level assignment (no parent except the module)
                if len(current_scope) == 0:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            global_variables[target.id] = astor.to_source(node.value).strip()
            elif isinstance(node, ast.FunctionDef):
                current_scope.append(node.name)  # Push function name
                function_body = astor.to_source(node).strip()
                # Remove the function name from the body
                function_body_lines = function_body.split('\n')
                if len(function_body_lines) > 1:
                    function_body_lines.pop(0)
                # Remove leading and trailing whitespace from each line
                function_body_lines = [line.strip() for line in function_body_lines]
                function_body = '\n'.join(function_body_lines)
                
                return_value = None
                
                # Check if the function has a return statement
                for child_node in node.body:
                    if isinstance(child_node, ast.Return):
                        return_value = astor.to_source(child_node.value).strip()
                        break
                
                # Remove return statements from the function body
                function_body_lines = [line for line in function_body_lines if not line.strip().startswith('return')]
                function_body = '\n'.join(function_body_lines)
                
                functions[node.name] = {
                    "arguments": [arg.arg for arg in node.args.args],
                    "returns": return_value,
                    "body": function_body
                }
            elif isinstance(node, ast.ClassDef):
                current_scope.append(node.name)  # Push class name
                methods = {}
                for child_node in node.body:
                    if isinstance(child_node, ast.FunctionDef):
                        method_body = astor.to_source(child_node).strip()
                        # Remove the function name from the body
                        method_body_lines = method_body.split('\n')
                        if len(method_body_lines) > 1:
                            method_body_lines.pop(0)
                        # Remove leading and trailing whitespace from each line
                        method_body_lines = [line.strip() for line in method_body_lines]
                        method_body = '\n'.join(method_body_lines)
                        method_info = {
                            "arguments": [arg.arg for arg in child_node.args.args],
                            "returns": None,  # Methods do not have return statements in their signature
                            "body": method_body
                        }
                        methods[child_node.name] = method_info
                        # Print method information
                        # print(f"Class: {node.name}, Method: {child_node.name}")
                        # print(json.dumps(method_info, indent=4))
                classes[node.name] = {
                    "methods": methods
                }

    # Return results as JSON
    return json.dumps({
        "imports": imports,
        "global_variables": global_variables,
        "functions": functions,
        "classes": classes
    }, indent=4)

# Example usage
if __name__ == "__main__":
    import re  # Import re here
    script_path = "test_script.py"  # Replace with your actual script path
    json_data = parse_script(script_path)
    print(json_data)
