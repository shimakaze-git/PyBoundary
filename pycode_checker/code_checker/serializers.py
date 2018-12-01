import os
import uuid
import threading
from rest_framework import serializers

from code_checker.domains import DownloadGithub
from code_checker.logics import code_analysis

TMP_DIR = os.environ.get('TMP_DIR', 'tmp')


class GitSerializer(serializers.Serializer):

    repo_list = {}

    account_name = serializers.CharField()
    repository = serializers.CharField()

    def __init__(self, data, uuid=None):
        super(GitSerializer, self).__init__(data=data)
        self.uuid = uuid

    def create(self, validated_data):
        account_name = validated_data.get('account_name')
        repository = validated_data.get('repository')

        response = None
        download_github = DownloadGithub(account_name, repository)
        print(download_github)
        # print(download_github)
        if download_github.is_exist():
            # logging
            thread_obj = threading.Thread(
                target=code_analysis(download_github, self.uuid, self.repo_list)
            )
            thread_obj.start()
            # code_analysis(download_github, self.uuid, self.repo_list)
        else:
            self.repo_list[self.uuid] = False
        return self.repo_list
