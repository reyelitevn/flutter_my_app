from github import Github
import re
import os
from datetime import datetime
# Initialize GitHub API client with the provided token
g = Github(os.getenv('GITHUB_TOKEN'))

# Dynamically get the current repository from the GITHUB_REPOSITORY environment variable
repo_name = os.getenv('GITHUB_REPOSITORY')  # Example: "your_username/your_repository"
repo = g.get_repo(repo_name)

# Categories for changelog entries
categories = [
    {"title": "Changes 🛠", "labels": ["major"]},
    {"title": "New Features 🎉", "labels": ["feature", "minor"]},
    {"title": "Fix Bugs 🐛", "labels": ["fix", "patch"]},
    {"title": "Enhancement ✅", "labels": ["enhance"]},
    {"title": "Documentation 📑", "labels": ["doc"]},
    {"title": "Other Changes", "labels": ["*"]},
]

# Get the most recent closed PRs
prs = repo.get_pulls(state='closed', sort='updated', direction='desc')

# Check for the most recent pull request with a 'changelog' label
changelog_label = 'changelog'
changelog_pr = prs[0] if prs.totalCount > 0 else None
if changelog_pr and any(label.name == changelog_label for label in changelog_pr.labels):
    # Extract and format the changelog from the PR body
    changelog = changelog_pr.body.replace('\r', '').replace('\n', '\\n')
else:
    target_version = os.getenv('TARGET_VERSION')
    version_bump_commit, previous_version_bump_commit = None, None

    # Find version bump commits in 'staging'
    commits = repo.get_commits(sha="staging")
    for commit in commits:
        if not version_bump_commit:
            match = re.search(r"\[Chore\] Bump version from ([\d\.]+\+\d+) to " + re.escape(target_version), commit.commit.message)
            if match:
                version_bump_commit = commit
                previous_version = match.group(1)  # This captures the version from which we bumped to the target version
                continue
        if version_bump_commit and '[Chore] Bump version from' in commit.commit.message:
            previous_version_bump_commit = commit
            break

    if not version_bump_commit or not previous_version_bump_commit:
        print(f"Version bump commits not found for {target_version}.")
        exit(1)

    # Check if the latest PR merged into 'staging' was from 'develop'
    latest_pr = prs[0] if prs.totalCount > 0 else None
    from_develop = latest_pr and latest_pr.head.ref == 'develop' and latest_pr.merged

    # Initialize a dictionary to hold categorized PRs
    categorized_prs = {category["title"]: [] for category in categories}

    # Include PRs merged into 'develop' if the latest 'staging' merge was from 'develop'
    develop_prs = []
    if from_develop:
        develop_prs = [pr for pr in repo.get_pulls(state='closed', base='develop', sort='updated') if pr.merged_at <= latest_pr.merged_at]

    # Combine PRs from 'develop' and direct merges into 'staging' within the version range
    countPRs = 0
    combined_prs = list(develop_prs)
    for pr in prs:
        if pr.merged:
            pr_merge_commit = repo.get_commit(pr.merge_commit_sha)
            combined_prs.append(pr)
        countPRs += 1
        # Check if countPRs has reached 50
        if countPRs == 20:
            break

    # Categorize PRs
    for pr in combined_prs:
        pr_labels = [label.name for label in pr.labels]
        for category in categories:
            if any(label in pr_labels for label in category["labels"]):
                categorized_prs[category["title"]].append(pr)
                break
        # else:
            # categorized_prs["Other Changes"].append(pr)

    # Generate the changelog text by category
    changelog = f""
    for category, prs in categorized_prs.items():
        if prs:  # Only include categories with PRs
            changelog += f"\n### {category}\n"
            for pr in prs:
                changelog += f"- {pr.title} #{pr.number}\n"

    if not any(categorized_prs.values()):
        changelog += "\n- Waiting for updates from the dev 🫣"

    # Output the changelog
    print(changelog.replace('\n', '\\n'))