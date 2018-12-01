#!/usr/bin/env python
import os
from code_checker.domains import code_check

TMP_DIR = os.environ.get('TMP_DIR', 'tmp')


def code_analysis(download_github_obj, uuid, repo_list):
    try:
        download_github_obj.run()
        # directory = '/home/ubuntu/workspace/pycode_checker/'

        owner = download_github_obj.owner
        repository = download_github_obj.repository
        app_directory = TMP_DIR + "/" + owner + "/" + repository
        print('app_directory : ', app_directory)
        # app_score_datas = code_check(app_directory=app_directory)
        # repo_list[uuid] = app_score_datas

    except Exception as e:
        # logging
        print(e)
