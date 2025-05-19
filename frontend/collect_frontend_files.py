import os

# Explicit filenames that affect the frontend appearance
files_to_collect = [
    "src/components/InputForm.jsx",
    "src/components/PollingStatus.jsx",
    "src/App.jsx",
    "src/main.jsx",
    "index.html",
    "postcss.config.cjs",
    "tailwind.config.cjs",
]

# Output file explicitly set
output_file = "frontend_appearance_files_content.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for file_name in files_to_collect:
        if os.path.exists(file_name):
            outfile.write(f"{'='*10} {file_name} {'='*10}\n\n")
            with open(file_name, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")
        else:
            outfile.write(f"{'='*10} {file_name} (Not Found) {'='*10}\n\n")

print(f"All specified file contents explicitly collected into {output_file}")
