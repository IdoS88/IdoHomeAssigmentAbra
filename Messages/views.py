from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import *
from .serializers import BaseUsersSerializer, CreateMessageInfoSerializer


@csrf_exempt
def get_all_users(request):
    if request.method == 'GET':
        users = Users.objects.all()
        serializer = BaseUsersSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def write_message(request):
    """
    List all code snippets, or create a new snippet.
    """
    # if request.method == 'GET':
    #    snippets = Snippet.objects.all()
    #   serializer = SnippetSerializer(snippets, many=True)
    #  return JsonResponse(serializer.data, safe=False)
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CreateMessageInfoSerializer(data=data)
        if serializer.is_valid():
            # Inspect or modify validated data if necessary
            validated_data = serializer.validated_data

            # Save the instance
            instance = serializer.save()

            # Now, it's safe to access serializer.data
            response_data = serializer.data
            return JsonResponse(response_data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    # if request.method == 'POST':
    #     data = JSONParser().parse(request)
    #     serializer = CreateMessageInfoSerializer(data=data)
    #
    #     if serializer.is_valid():
    #         serializer.save()
    #         print('valid')
    #         return JsonResponse(serializer.data, status=201)
    #     return JsonResponse(serializer.errors, status=400)
