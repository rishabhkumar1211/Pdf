import os, re, requests
from datetime import datetime, timezone

REPO_NAME   = os.environ.get("REPO_NAME", "")
GH_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
README_PATH = "README.md"
MAX_COMMITS = 10
HEADERS = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}

def gh_get(path):
    r = requests.get(f"https://api.github.com/{path.lstrip('/')}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def build_badges(repo):
    owner, name = REPO_NAME.split("/", 1)
    url  = repo.get("html_url", f"https://github.com/{REPO_NAME}")
    br   = repo.get("default_branch", "main")
    lic  = (repo.get("license") or {}).get("spdx_id", "")
    date = datetime.now(timezone.utc).strftime("%Y--%m--%d")
    badges = [
        f'[![Stars](https://img.shields.io/github/stars/{owner}/{name}?style=flat-square&color=yellow)]({url}/stargazers)',
        f'[![Forks](https://img.shields.io/github/forks/{owner}/{name}?style=flat-square&color=blue)]({url}/network/members)',
        f'[![Last Commit](https://img.shields.io/github/last-commit/{owner}/{name}/{br}?style=flat-square&color=green)]({url}/commits/{br})',
        f'[![Issues](https://img.shields.io/github/issues/{owner}/{name}?style=flat-square&color=red)]({url}/issues)',
        f'![Updated](https://img.shields.io/badge/last--synced-{date}-informational?style=flat-square)',
    ]
    if lic:
        badges.append(f'[![License](https://img.shields.io/github/license/{owner}/{name}?style=flat-square)]({url}/blob/{br}/LICENSE)')
    return "\n".join(badges)

def build_changelog(commits):
    if not commits:
        return "_No commits found._"
    url   = f"https://github.com/{REPO_NAME}"
    lines = ["| Date | Commit | Message |", "|------|--------|---------|"]
    for c in commits:
        sha  = c.get("sha", "")[:7]
        msg  = (c.get("commit", {}).get("message", "") or "").splitlines()[0]
        for p in ["[skip ci]", "docs:", "chore:", "ci:", "build:"]:
            msg = msg.replace(p, "").strip()
        msg  = (msg[:72] + "…") if len(msg) > 72 else msg
        date = (c.get("commit", {}).get("committer") or {}).get("date", "")[:10] or "—"
        lines.append(f"| {date} | [`{sha}`]({url}/commit/{c['sha']}) | {msg} |")
    lines.append(f"\n_Auto-generated on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_")
    return "\n".join(lines)

def patch(content, tag, body):
    p, n = re.subn(rf"(<!-- {tag}:START -->).*?(<!-- {tag}:END -->)",
                   rf"\1\n{body}\n\2", content, flags=re.DOTALL)
    if not n:
        print(f"  WARNING: {tag} markers not found — skipping.")
    return p

def main():
    if not REPO_NAME or not GH_TOKEN:
        raise SystemExit("Missing REPO_NAME or GITHUB_TOKEN")
    repo = gh_get(f"repos/{REPO_NAME}")
    br   = repo.get("default_branch", "main")
    try:
        commits = gh_get(f"repos/{REPO_NAME}/commits?sha={br}&per_page={MAX_COMMITS}")
    except Exception:
        commits = gh_get(f"repos/{REPO_NAME}/commits?per_page={MAX_COMMITS}")
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content = patch(content, "BADGES",    build_badges(repo))
    content = patch(content, "CHANGELOG", build_changelog(commits if isinstance(commits, list) else []))
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated successfully.")

if __name__ == "__main__":
    main()
