import requests
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess

# === CONFIGURATION ===
GITHUB_USERNAME = "Dippp10"          # Replace with your GitHub username
GITHUB_TOKEN = "" # Needs 'repo' scope if private repos
REPO_PATH = "/path/to/your/local/repo"     # Local clone of your repo
BADGE_FILE = os.path.join(REPO_PATH, "openssf-badge.svg")
README_FILE = os.path.join(REPO_PATH, "README.md")  # Optional if you embed badge

# === FUNCTIONS ===
def fetch_repos():
    """Fetch all repos with pagination."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"}).json()
        if not response:
            break
        repos.extend([repo['name'] for repo in response])
        page += 1
    return repos

def fetch_score(repo):
    """Fetch OpenSSF Scorecard score for a repo."""
    url = f"https://api.securityscorecards.dev/projects/github.com/{GITHUB_USERNAME}/{repo}"
    r = requests.get(url)
    if r.status_code == 200:
        score = r.json().get("score")
        if score is not None:
            return float(score)
    return None

def generate_badge(avg_score):
    """Generate badge SVG via shields.io."""
    if avg_score >= 9:
        color = "brightgreen"
    elif avg_score >= 7:
        color = "green"
    elif avg_score >= 4:
        color = "yellow"
    else:
        color = "red"
    badge_url = f"https://img.shields.io/badge/OpenSSF-AverageScore-{avg_score}-{color}.svg"
    badge_svg = requests.get(badge_url).text
    with open(BADGE_FILE, "w") as f:
        f.write(badge_svg)
    print(f"Badge saved to {BADGE_FILE}")

def commit_badge():
    """Commit and push the badge to the repository."""
    subprocess.run(["git", "-C", REPO_PATH, "add", BADGE_FILE])
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", "Update OpenSSF account badge"])
    subprocess.run(["git", "-C", REPO_PATH, "push"])

# === MAIN ===
def main():
    print("Fetching all repositories...")
    repos = fetch_repos()
    print(f"Total repos found: {len(repos)}")

    print("Fetching OpenSSF scores in parallel...")
    total_score = 0
    valid_count = 0
    with ThreadPoolExecutor(max_workers=50) as executor:
        for score in executor.map(fetch_score, repos):
            if score is not None:
                total_score += score
                valid_count += 1

    avg_score = round(total_score / valid_count, 2) if valid_count else 0
    print(f"Average OpenSSF Score: {avg_score}")

    print("Generating badge...")
    generate_badge(avg_score)

    print("Committing badge to repo...")
    commit_badge()
    print("Done.")

if __name__ == "__main__":
    main()
