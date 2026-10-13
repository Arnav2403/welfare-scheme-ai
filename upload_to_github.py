
import os
import subprocess
import sys

# Change this to your GitHub username and repository name
GITHUB_USERNAME = "Arnav2403"
REPO_NAME = "welfare-scheme-ai"

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))

def run(command):
    print(f"\n> {' '.join(command)}")
    result = subprocess.run(command, cwd=PROJECT_FOLDER)
    if result.returncode != 0:
        sys.exit("Command failed. Fix the error above and run the script again.")

# Check that Git is installed
try:
    subprocess.run(
        ["git", "--version"],
        check=True,
        capture_output=True
    )
except (FileNotFoundError, subprocess.CalledProcessError):
    sys.exit("Git is not installed. Install it from https://git-scm.com/")

# Prevent common sensitive/local files from being uploaded
gitignore = os.path.join(PROJECT_FOLDER, ".gitignore")
ignore_entries = [
    "venv/",
    ".venv/",
    "__pycache__/",
    "*.py[cod]",
    ".env",
    ".git/",
]

existing = ""
if os.path.exists(gitignore):
    with open(gitignore, "r", encoding="utf-8") as file:
        existing = file.read()

with open(gitignore, "a", encoding="utf-8") as file:
    for entry in ignore_entries:
        if entry not in existing.splitlines():
            file.write(entry + "\n")

# Check for a repository URL
if GITHUB_USERNAME == "YOUR_GITHUB_USERNAME":
    sys.exit("Edit GITHUB_USERNAME at the top of this script first.")

repo_url = (
    f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
)

# Initialize Git if needed
if not os.path.isdir(os.path.join(PROJECT_FOLDER, ".git")):
    run(["git", "init"])

# Stage project files and show what's going to be uploaded
run(["git", "add", "."])
run(["git", "status", "--short"])

print("\nIMPORTANT: Review the files above.")
print("Ensure no passwords, API keys, .env files, or private data are staged.")
answer = input("Type UPLOAD to continue: ")

if answer != "UPLOAD":
    sys.exit("Upload cancelled. Your files have not been pushed.")

# Commit
subprocess.run(
    ["git", "config", "user.name"],
    cwd=PROJECT_FOLDER,
    capture_output=True,
    check=False
)

result = subprocess.run(
    ["git", "diff", "--cached", "--quiet"],
    cwd=PROJECT_FOLDER
)

if result.returncode == 0:
    print("No staged changes to commit.")
else:
    run(["git", "add", "."])
    run(["git", "commit", "-m", "Initial commit: Welfare Scheme AI"])

# Set branch and remote
run(["git", "branch", "-M", "main"])

remote = subprocess.run(
    ["git", "remote", "get-url", "origin"],
    cwd=PROJECT_FOLDER,
    capture_output=True,
    text=True
)

if remote.returncode == 0:
    run(["git", "remote", "set-url", "origin", repo_url])
else:
    run(["git", "remote", "add", "origin", repo_url])

# Push to GitHub; authenticate through Git Credential Manager/browser if prompted
run(["git", "push", "-u", "origin", "main"])

print("\nUpload completed successfully!")
print(f"Repository: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
