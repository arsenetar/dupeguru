#!/usr/bin/env python3
import sys
import os
import re
from datetime import date
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(PROJECT_ROOT, "core", "__init__.py")
CHANGELOG_FILE = os.path.join(PROJECT_ROOT, "help", "changelog")


def get_current_version():
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in core/__init__.py")
    return match.group(1)


def get_changelog_latest_version():
    with open(CHANGELOG_FILE, "r") as f:
        first_line = f.readline().strip()
    match = re.match(r"===\s*([^\s(]+)", first_line)
    if not match:
        return None
    return match.group(1)


def bump_version(new_version):
    # Validate version format (e.g. 4.3.2)
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print(f"Error: version '{new_version}' is not in semantic versioning format (e.g. 4.3.2)")
        sys.exit(1)

    # 1. Update core/__init__.py
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    updated_content = re.sub(r'__version__\s*=\s*["\'][^"\']+["\']', f'__version__ = "{new_version}"', content)
    with open(VERSION_FILE, "w") as f:
        f.write(updated_content)
    print(f"Updated version in core/__init__.py to {new_version}")

    # 2. Update help/changelog
    with open(CHANGELOG_FILE, "r") as f:
        changelog_lines = f.readlines()

    today = date.today().strftime("%Y-%m-%d")
    header = f"=== {new_version} ({today})\n* New release\n\n"

    # Check if the latest version in changelog is already the new version
    latest_version = get_changelog_latest_version()
    if latest_version == new_version:
        print(f"Changelog already has header for {new_version}")
    else:
        changelog_lines.insert(0, header)
        with open(CHANGELOG_FILE, "w") as f:
            f.writelines(changelog_lines)
        print(f"Prepended header for {new_version} to help/changelog")


def run_checks():
    # 1. Run tests
    print("Running unit tests...")
    res = subprocess.run(["env/bin/pytest", "core", "hscommon"])
    if res.returncode != 0:
        print("Error: Unit tests failed. Release aborted.")
        sys.exit(1)
    print("All unit tests passed successfully!")

    # 2. Check git status
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if res.stdout.strip():
        print("Warning: Git working directory is not clean. Commit or stash changes first.")


def git_release(new_version):
    # Ensure git workspace is clean
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    # Exclude untracked files
    dirty_files = [line for line in res.stdout.splitlines() if not line.startswith("??")]
    if dirty_files:
        print("Error: Git repository has uncommitted modifications. Please stash or commit them.")
        sys.exit(1)

    # Bump version
    bump_version(new_version)

    # Run tests
    run_checks()

    # Commit
    print("Committing release changes...")
    subprocess.run(["git", "add", VERSION_FILE, CHANGELOG_FILE])
    subprocess.run(["git", "commit", "-m", f"release: bump version to {new_version}"])

    # Tag
    tag_name = f"v{new_version}"
    print(f"Creating Git tag {tag_name}...")
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"])
    print(f"Release v{new_version} committed and tagged successfully!")
    print("To push to remote, run: git push origin main --tags")


def print_help():
    print("dupeGuru Release Helper")
    print("Usage:")
    print("  python scripts/release_helper.py status           - Show current version and check alignment")
    print("  python scripts/release_helper.py bump <version>   - Bump version files and prep changelog")
    print("  python scripts/release_helper.py release <version> - Verify tests, bump, commit and tag git release")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "status":
        curr = get_current_version()
        latest_ch = get_changelog_latest_version()
        print(f"Current version in core/__init__.py: {curr}")
        print(f"Latest version in help/changelog:    {latest_ch}")
        if curr == latest_ch:
            print("Status: Version and Changelog are aligned!")
        else:
            print("Status: WARNING! Version and Changelog are out of sync!")
    elif cmd == "bump":
        if len(sys.argv) < 3:
            print("Error: Please provide a version number (e.g. bump 4.3.2)")
            sys.exit(1)
        bump_version(sys.argv[2])
    elif cmd == "release":
        if len(sys.argv) < 3:
            print("Error: Please provide a version number (e.g. release 4.3.2)")
            sys.exit(1)
        git_release(sys.argv[2])
    else:
        print_help()


if __name__ == "__main__":
    main()
