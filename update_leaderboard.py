import os
from github import Github  # PyGithub library
from collections import defaultdict

# Auth (GitHub Token in Secrets)
g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

def calculate_score(issue):
    score = 0
    # Points for labels
    if "bug" in [label.name for label in issue.labels]:
        score += 10
    if "feature" in [label.name for label in issue.labels]:
        score += 20
    # Points for reaction votes
    score += issue.get_reactions().totalCount * 2
    # Speed bonus (closed in <24h)
    if (issue.closed_at - issue.created_at).seconds < 86400:
        score += 15
    return score

# Fetch closed issues and calculate scores
scores = defaultdict(int)
for issue in repo.get_issues(state="closed"):
    if issue.pull_request:  # Skip PRs
        continue
    solver = issue.assignee.login if issue.assignee else "Unknown"
    scores[solver] += calculate_score(issue)

# Generate Leaderboard Markdown
leaderboard = "| Rank | User | Points |\n|------|------|--------|\n"
for idx, (user, points) in enumerate(sorted(scores.items(), key=lambda x: -x[1]), 1):
    leaderboard += f"| {idx} | @{user} | {points} |\n"

# Update README
with open("README.md", "r") as f:
    content = f.read()

new_content = content.replace(
    "<!-- LEADERBOARD_START -->\n<!-- LEADERBOARD_END -->",
    f"<!-- LEADERBOARD_START -->\n{leaderboard}\n<!-- LEADERBOARD_END -->"
)

with open("README.md", "w") as f:
    f.write(new_content)