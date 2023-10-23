import os
import time
from git import Repo, Git

_repo_cache = {}

def _get_repo(path: str) -> Git:
    """
    Get the git repository of the path.
    """

    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if path not in _repo_cache:
        _repo_cache[path] = Repo(path, search_parent_directories=True).git
        
    return _repo_cache[path]

def get_latest_commit_timestamp(path: str) -> int:
    """
    Get the timestamp of the latest commit of the path.

    If no commit is found, return the current timestamp.
    """
    
    realpath = os.path.realpath(path)
    repo = _get_repo(realpath)

    commit_timestamp = repo.log(realpath, format="%at", n=1)

    if commit_timestamp == "":
        commit_timestamp = time.time()

    return int(commit_timestamp)

if __name__ == "__main__":
    print("Stamp: %d" % get_latest_commit_timestamp("./mkdocs_turing_plugins/utils/git_utils.py"))
    print("Stamp: %d" % get_latest_commit_timestamp("./mkdocs_turing_plugins/utils/markdown_utils.py"))
