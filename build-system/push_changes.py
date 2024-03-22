import subprocess
import sys

def push_changes(github_token, github_repository, branch):
    try:
        # Constructing the GitHub URL for authentication
        github_url = f"https://{github_token}:x-oauth-basic@github.com/{github_repository}"
        subprocess.run(['git', 'push', github_url, f'HEAD:{branch}'], check=True)
    except subprocess.CalledProcessError:
        print("Push failed, attempting to push using Python...")
        push_with_python(github_token, github_repository, branch)

def push_with_python(github_token, github_repository, branch):
    from git import Repo

    try:
        repo = Repo('.')
        origin = repo.remote('origin')
        origin.push(refspec=f'HEAD:{branch}', tags=True)
        print("Push successful!")
    except Exception as e:
        print("Error occurred while pushing using Python:", e)

if __name__ == "__main__":
    # Retrieve GitHub token, repository, and branch from command-line arguments
    github_token = sys.argv[1]
    github_repository = sys.argv[2]
    branch = sys.argv[3]
    
    push_changes(github_token, github_repository, branch)