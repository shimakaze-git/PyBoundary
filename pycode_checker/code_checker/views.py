from django.shortcuts import render

# Create your views here.

import uuid

from code_checker.serializers import GitSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GitViewSet(APIView):

    def get(self, request, pk, format=None):

        serializer = GitSerializer(data=None)
        if pk in serializer.repo_list:
            response_data = serializer.repo_list[pk]
            serializer.repo_list.pop(pk)
            return Response(response_data)
        else:
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    def post(self, request, format=None):

        # create uuid
        u4 = str(uuid.uuid4())

        serializer = GitSerializer(data=request.data, uuid=u4)

        # validation_check
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data)
            # curl -X POST http://127.0.0.1:8000/api/git/ --data 'account_name=test&repository_url=test'

            response = {
                'uuid': u4
            }
            return Response(
                response,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
