#!/usr/bin/env python
import os
import subprocess
import mimetypes
from pathlib import Path

from radon.cli.harvest import CCHarvester
from radon.cli import Config
from radon import complexity

from code_checker.helper import get_repository, get_sha_for_tag, download_directory
# from helper import get_repository, get_sha_for_tag, download_directory
from github import Github

TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN', 'test')
TMP_DIR = os.environ.get('TMP_DIR', 'tmp')


class DownloadGithub:

    github = Github(TOKEN)

    def __init__(self, owner, repository, branch="master"):
        self.owner = owner
        self.repository = repository
        self.branch = branch

        self.__repo = get_repository(
            self.owner, self.repository
        )

    def run(self):
        self.start_download()

    def start_download(self):
        try:
            sha = get_sha_for_tag(self.__repo, self.branch)

            server_path = "./"
            download_directory(self.__repo, sha, server_path, save_dir=TMP_DIR)
        except Exception as e:
            # logging
            print(e)

    def is_exist(self):
        if self.__repo:
            return True
        else:
            # logging
            return False


class RadonInterface(object):

    def __init__(self):

        self.config = Config(
            min="A",
            max="F",
            exclude=None,
            ignore=False,
            show_complexity=True,
            average=False,
            total_average=False,
            order=getattr(complexity, "SCORE", getattr(complexity, 'SCORE')),
            no_assert=False,
            show_closures=False,
        )

        self.cc_output = None
        self.mi_output = None

        self.paths = None

    def start(self, paths):

        self.paths = paths
        cc_harvester = CCHarvester(
            paths,
            self.config
        )
        self.cc_output = cc_harvester._to_dicts()
        # self.mi_output = cc_harvester._to_dicts()

    def serialize(self):

        return {
            'cc': self.cc_serialize(),
            'mi': None
        }

    def cc_serialize(self):

        serialize_cc_output = []
        
        if self.cc_output:
            for cc in self.cc_output[self.paths[0]]:
                if cc['type'] is not 'method':
                    serialize_cc_output.append(cc)
        return serialize_cc_output

class CodeChecker(object):

    def __init__(self, runner):
        self.runnner = runner

    def code_check(self, file_path):
        self.runnner.start(file_path)
        serialize_data = self.runnner.serialize()
        return serialize_data


class Score_Calculation(object):

    def __init__(self, datas):
        """ Constructor """

        self.datas = datas
        self.new_datas = []

        self.cc_file_count = 0
        self.mi_file_count = 0

        self.cc_all_average = 0
        self.ml_all_average = 0

    def run_average(self):
        """ Average """

        cc_average_all = 0
        mi_average_all = 0

        for data in self.datas:
            cc_datas = data['data']['cc']
            mi_datas = data['data']['mi']

            cc_average = 0.0
            mi_average = 0.0

            if cc_datas:
                cc_average = self.cc_datas_average(
                    cc_datas
                )
                data['data']['cc_average'] = cc_average
                cc_average_all += cc_average

            if mi_datas:
                mi_average = 1.0
                mi_average_all += mi_average

            """ update average """
            data['data']['cc_average'] = cc_average
            data['data']['mi_average'] = mi_average
            self.new_datas.append(data)
        
        """ all average """
        self.all_average(
            cc_average_all,
            mi_average_all
        )

    def serialize(self):
        return {
            'cc_average': self.cc_all_average,
            'mi_average': self.ml_all_average,
            'datas': self.new_datas
        }

    def cc_datas_average(self, cc_datas):
        """ cc_datas_average """

        all_complexity = 0
        cc_datas_len = len(cc_datas)

        self.cc_file_count += 1

        for cc_data in cc_datas:
            complexity = cc_data['complexity']
            all_complexity += complexity

        return (all_complexity/cc_datas_len)

    def mi_datas_average(self, mi_datas):
        pass

    def all_average(
        self,
        cc_average_all,
        mi_average_all
    ):

        if self.cc_file_count:
            self.cc_all_average = (
                cc_average_all/self.cc_file_count
            )

        if self.mi_file_count:
            self.ml_all_average = (
                mi_average_all/self.mi_file_count
            )

# main
def code_check(app_directory):
    """ start process """

    path_list = Path(app_directory)

    code_score_list = []
    for file_path in list(path_list.glob("**/*.py")):
        file_path = str(file_path)
        mime = mimetypes.guess_type(file_path)

        mime_type = mime[0]
        if mime_type == 'text/x-python':

            # runnner_obj = RadonRunner()
            runnner_obj = RadonInterface()

            code_checker = CodeChecker(runnner_obj)
            data = code_checker.code_check(
                [file_path]
            )

            code_score = {
                "file_path": file_path,
                "data": data
            }
            code_score_list.append(code_score)

    """ cc & mi average Serialize"""
    score_calculation = Score_Calculation(
        code_score_list
    )
    score_calculation.run_average()
    app_score_datas = score_calculation.serialize()

    return app_score_datas


# if __name__ == '__main__':
#     directory = '/home/ubuntu/workspace/pycode_checker/'
#     app_score_datas = code_check(app_directory=directory)
#     print(app_score_datas)
