# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github galaxy_ng' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

import argparse
import os
import textwrap

from git import Repo
from git.exc import GitCommandError


helper = textwrap.dedent(
    """\
        Stage the changelog for a release on master branch.

        Example:
            $ python .github/workflows/scripts/stage-changelog-for-default-branch.py 3.4.0

    """
)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=helper)

parser.add_argument(
    "release_version",
    type=str,
    help="The version string for the release.",
)

args = parser.parse_args()

release_version_arg = args.release_version

release_path = os.path.dirname(os.path.abspath(__file__))
plugin_path = release_path.split("/.github")[0]

print(f"\n\nRepo path: {plugin_path}")
repo = Repo(plugin_path)

changelog_commit = None
# Look for a commit with the requested release version
for commit in repo.iter_commits():
    if f"{release_version_arg} changelog" == commit.message.split("\n")[0]:
        changelog_commit = commit
        break
    if f"Add changelog for {release_version_arg}" == commit.message.split("\n")[0]:
        changelog_commit = commit
        break

if not changelog_commit:
    raise RuntimeError("Changelog commit for {release_version_arg} was not found.")

git = repo.git
git.stash()
git.checkout("origin/master")
try:
    git.cherry_pick(changelog_commit.hexsha)
except GitCommandError:
    git.add("CHANGES/")
    # Don't try opening an editor for the commit message
    with git.custom_environment(GIT_EDITOR="true"):
        git.cherry_pick("--continue")
git.reset("origin/master")

# Do not remove changelog entries
msg = repo.commit().message
git.reset("HEAD~1")
git.add("CHANGES.rst")
git.commit("-m", msg)
git.stash()
