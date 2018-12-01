#!/usr/bin/env python
'''
Created on 2018/11/30

@author: shimakaze-git
'''

import os
from github import Github
from github import GithubException
import base64
import logging


TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
 
github_obj = Github(TOKEN)


def get_repository(owner, repository_name):
    repo_url = owner + "/" + repository_name
    try:
        repo = github_obj.get_repo(repo_url)
        return repo
    except (GithubException, IOError) as e:
        # logging
        print(e)
        return None

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def make_dir(path):
    path_list = path.split('/')
    dir_len = len(path_list)

    dir_name = '/'.join(
        [str(path_list[i]) for i in range(len(path_list)-1)]
    )
    return dir_name

def get_sha_for_tag(repository, tag):
    """
    Returns a commit PyGithub object for the specified repository and tag.
    """
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]

    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with that name')
    return matched_tags[0].commit.sha


def download_directory(repository, sha, server_path, save_dir=None):
    """
    Download all contents at server_path with commit tag sha in
    the repository.
    """

    logging.debug("server_path %s" % server_path)
    contents = repository.get_dir_contents(server_path, ref=sha)

    for content in contents:
        logging.debug("Processing %s" % content.path)
        if content.type == 'dir':
            download_directory(repository, sha, content.path, save_dir)
        else:
            try:
                # print(repository.get_languages())
                owner = repository.owner.login

                path = content.path
                file_content = repository.get_contents(path, ref=sha)

                dir_name = make_dir(owner + "/" + repository.name + "/" + path)
                if dir_name:
                    my_makedirs(save_dir + "/" + dir_name)

                save_path = save_dir + "/" + owner + "/" + repository.name + "/" + path
                file_data = base64.b64decode(file_content.content).decode('utf-8')
                with open(save_path, mode='w') as file:
                    file.write(file_data)

            except (GithubException, IOError) as exc:
                logging.error('Error processing %s: %s', content.path, exc)
                raise exc

                # https://sookocheff.com/post/tools/downloading-directories-of-code-from-github-using-the-github-api/
                # https://note.nkmk.me/python-os-mkdir-makedirs/
                # https://note.nkmk.me/python-file-io-open-with/
                # https://pygithub.readthedocs.io/en/latest/examples/Repository.html