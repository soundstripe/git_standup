from datetime import datetime, timedelta
from itertools import chain
from operator import attrgetter
from pathlib import Path

import click
import pytz
from git import Repo
from tqdm import tqdm


@click.command()
@click.option(
    '--path', '-p',
    type=click.Path(dir_okay=True, file_okay=False),
    required=True,
    multiple=True,
    help='Scan this path for git repos'
)
@click.option(
    '--exclude', '-x',
    type=click.Path(dir_okay=True, file_okay=False),
    multiple=True,
    help='Scan this path for git repos'
)    
def main(path=(), exclude=()):
    """
    Display latest commits from all repos found in specified directories
    """
    roots = set(chain.from_iterable(Path(p).glob('**/.git') for p in path))
    exclude = set(chain.from_iterable(Path(p).glob('**/.git') for p in exclude))
    git_folders = [p.parent for p in roots ^ exclude]
    progress = tqdm(git_folders, 'gathering commits')
    commits = get_latest_commits(progress)

    for stem, commit in commits:
        ts, committer, msg = commit.committed_datetime, commit.committer, commit.message.strip()
        print(f'{ts} {stem:<20} {committer!s:<20} {msg}')

def get_latest_commits(git_folders):
    commits = []
    for f in git_folders:
        r = Repo(f)
        commits.extend((f.stem, c) for c in list(r.iter_commits(max_count=50)) if is_recent(c))
    commits.sort(key=lambda c: c[1].committed_datetime)
    return commits

def is_recent(commit, delta=timedelta(days=50)):
    return datetime.now(pytz.utc) - commit.committed_datetime < delta

if __name__ == "__main__":
    main()
