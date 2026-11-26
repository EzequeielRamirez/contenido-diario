"""Sube el video a una rama 'media-<slot>' del mismo repo (público) para que Meta pueda descargarlo por URL."""
import os, subprocess, shutil, tempfile
def sh(*a, cwd=None): subprocess.run(a, check=True, cwd=cwd, stdout=subprocess.DEVNULL)
def upload(path, slot):
    repo = os.environ["GITHUB_REPOSITORY"]; tok = os.environ["GITHUB_TOKEN"]
    branch = f"media-{slot}"; name = os.path.basename(path)
    d = tempfile.mkdtemp(); sh("git", "init", "-q", cwd=d)
    sh("git", "checkout", "-q", "-b", branch, cwd=d)
    shutil.copy(path, f"{d}/{name}")
    sh("git", "-c", "user.name=bot", "-c", "user.email=bot@users.noreply.github.com", "add", ".", cwd=d)
    sh("git", "-c", "user.name=bot", "-c", "user.email=bot@users.noreply.github.com", "commit", "-q", "-m", f"media {name}", cwd=d)
    sh("git", "push", "-q", "--force", f"https://x-access-token:{tok}@github.com/{repo}.git", branch, cwd=d)
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{name}"
