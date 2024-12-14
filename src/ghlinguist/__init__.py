from __future__ import annotations
import subprocess
import logging
from pathlib import Path
import shutil

EXE = shutil.which("github-linguist")
if not EXE:
    raise ImportError("GitHub Linguist not found, did you install it per README?")

GIT = shutil.which("git")
if not GIT:
    raise ImportError("Git not found")


def linguist(path: Path, rtype: bool = False) -> str | list[tuple[str, str]]:
    """runs Github Linguist Ruby script"""

    path = Path(path).expanduser()

    if not checkrepo(path):
        return None

    ret = subprocess.check_output([EXE, str(path)], text=True).split("\n")

    # %% parse percentage
    lpct = []

    for line in ret:
        L = line.split()
        if not L:  # EOF
            break
            
        lang = ""
        # Loop over the elements of L starting from the end and append the elements until we reach the number of lines
        for i in range(len(L) - 1, -1, -1):
            if L[i].isdigit():
                break
            if lang:
                lang = L[i] + " " + lang
            else:
                lang = L[i]

        lpct.append((lang, L[0][:-1]))


    if rtype:
        return lpct[0][0]

    return lpct


def checkrepo(path: Path) -> bool:
    """basic check for healthy Git repo ready for Linguist to analyze"""

    path = Path(path).expanduser()

    if not (path / ".git").is_dir():
        logging.error(
            f'{path} does not seem to be a Git repository, and Linguist only works on files after "git commit"'
        )
        return False

    # %% detect uncommited (dirty)
    ret = subprocess.check_output([GIT, "-C", str(path), "status", "--porcelain"], text=True)

    ADD = {"A", "?"}
    MOD = "M"

    for line in ret.split("\n"):
        L = line.split()
        if not L:
            continue

        if ADD.intersection(L[0]) or (MOD in L[0] and L[1] == ".gitattributes"):
            logging.warning(
                f' {path} has uncommited changes: \n\n{ret}\n Linguist only works on files after "git commit"'
            )
            return False

    return True
