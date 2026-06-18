import requests

owner = "ygyuvrajgupta-dev"
repo = "essarfab-website"

# Get default branch
repo_info = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}"
).json()

branch = repo_info["default_branch"]

# Get full tree recursively
tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
tree_data = requests.get(tree_url).json()

file_count = sum(1 for item in tree_data["tree"] if item["type"] == "blob")

print("Total files:", file_count)