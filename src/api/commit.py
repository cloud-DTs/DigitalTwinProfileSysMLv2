from .ApiModels.Commit import Commit
import logging
from ..utils import globals
import requests
import datetime
def get_commits(project_id:str) -> list[Commit]:
    logging.info(f"Fetching commits from project with ID: {project_id} from host: {globals.get_host()}")
    try:
        response = requests.get(f"{globals.get_host()}/projects/{project_id}/commits")
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Error fetching commits: {e}")
        
    commits_data = response.json()
    commits = [Commit.fromDict(commit) for commit in commits_data]
    logging.debug(f"Retrieved {len(commits)} commits for project ID: {project_id}")
    return commits

def get_last_commit(project_id:str) -> Commit:
    commits = get_commits(project_id)
    if not commits:
        logging.error(f"No commits found for project ID: {project_id}")
        return None
    last_commit = max(commits, key=lambda c: datetime.datetime.fromisoformat(c.created))
    logging.debug(f"Last commit ID: {last_commit.id}, Created at: {last_commit.created}")
    return last_commit