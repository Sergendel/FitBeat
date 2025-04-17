import os


def generate_folder_structure(root, exclude_dirs, exclude_files):
    structure_lines = []

    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        files = [f for f in files if not any(f.endswith(ext) for ext in exclude_files)]

        level = current_root.replace(root, '').count(os.sep)
        indent = '|   ' * level + '|-- '
        structure_lines.append(f"{indent}{os.path.basename(current_root) if level > 0 else ''}")

        for file in files:
            file_indent = '|   ' * (level + 1) + '|-- '
            structure_lines.append(f"{file_indent}{file}")

    return '\n'.join(line for line in structure_lines if line.strip())


def list_python_files(project_root, output_file):
    exclude_dirs = {'.git', 'downloaded_tracks', '.idea', 'genius_corpus', '__pycache__'}
    exclude_files_ext = {'.pyc', '.mp3', '.txt'}

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write folder structure
        folder_structure = generate_folder_structure(project_root, exclude_dirs, exclude_files_ext)
        outfile.write("Project Folder Structure:\n")
        outfile.write(folder_structure)
        outfile.write("\n\n")

        # Walk through project directory recursively
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.relpath(os.path.join(root, file), project_root)
                    outfile.write(f"{'=' * 80}\n")
                    outfile.write(f"File: {file_path}\n")
                    outfile.write(f"{'=' * 80}\n")

                    # Write file contents
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as pyfile:
                        outfile.write(pyfile.read())
                        outfile.write("\n\n")


# Example usage
project_root = r'C:\work\INTERVIEW_PREPARATION\FitBeat'  # replace with your project's root path
output_file = 'project_description.txt'
list_python_files(project_root, output_file)

print(f"All Python files and the folder structure have been listed in {output_file}")
