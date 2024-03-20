from github import Github
import re
import os
from datetime import datetime
# Initialize GitHub API client with the provided token
g = Github(os.getenv('GITHUB_TOKEN'))

# Dynamically get the current repository from the GITHUB_REPOSITORY environment variable
repo_name = os.getenv('GITHUB_REPOSITORY')  # Example: "your_username/your_repository"
repo = g.get_repo(repo_name)

categories = [
    {"title": "Changes 🛠", "labels": ["major"]},
    {"title": "New Features 🎉", "labels": ["feature", "minor"]},
    {"title": "Fix Bugs 🐛", "labels": ["fix", "patch"]},
    {"title": "Enhancement ✅", "labels": ["enhance"]},
    {"title": "Documentation 📑", "labels": ["doc"]},
    {"title": "Other Changes", "labels": ["*"]},
]

target_version = os.getenv('TARGET_VERSION')
version_pattern = re.compile(r"\[Chore\] Bump version from [\d\.]+\+\d+ to " + re.escape(target_version))
version_bump_commit = None

commits = repo.get_commits(sha="staging")
for commit in commits:
    if version_pattern.search(commit.commit.message):
        version_bump_commit = commit
        print(f"Found version bump commit: {commit.sha} - {commit.commit.message}")
        break

if not version_bump_commit:
    print(f"Version bump to {target_version} not found.")
    exit(1)

prs = repo.get_pulls(base="staging", state="closed", sort="created", direction="desc")
# Initialize a dictionary to hold categorized PRs
categorized_prs = {category["title"]: [] for category in categories}

# Process each PR to categorize it based on labels
for pr in prs:
    if pr.merged:
        pr_labels = [label.name for label in pr.labels]
        # Fetch the PR's last commit date
        pr_last_commit_date = pr.get_commits().reversed[0].commit.committer.date
        # Ensure PR is after the version bump commit
        if pr_last_commit_date > version_bump_commit.commit.committer.date:
            # Categorize the PR based on its labels
            categorized = False
            for category in categories:
                if category["title"] == "Other Changes" or any(label in pr_labels for label in category["labels"]):
                    categorized_prs[category["title"]].append(pr)
                    categorized = True
                    break
            if not categorized:
                categorized_prs["Other Changes"].append(pr)

changelog = f"## Changelog since version {target_version}\n"
is_changelog_empty = True
for category, prs in categorized_prs.items():
    if prs:  # Only include categories with PRs
        is_changelog_empty = False
        changelog += f"\n### {category}\n"
        for pr in prs:
            changelog += f"- {pr.title} #{pr.number}\n"

if is_changelog_empty:
    changelog += "\n- Em chịu, không biết có update gì hong, đợi dev vào report nha mn :hehe-dog:"

print(changelog)