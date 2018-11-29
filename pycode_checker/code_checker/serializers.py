import uuid
from rest_framework import serializers


class GitSerializer(serializers.Serializer):

    repo_list = {}

    account_name = serializers.CharField()
    repository = serializers.CharField()

    def __init__(self, data, uuid=None):
        super(GitSerializer, self).__init__(data=data)
        self.uuid = uuid

    def create(self, validated_data):
        print(validated_data)
        # print(**validated_data)
        print(self.uuid)
        self.repo_list[self.uuid] = []

        # return Snippet.objects.create(**validated_data)
        return self.repo_list