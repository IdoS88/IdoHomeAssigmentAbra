from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CreateMessageSerializer


# @csrf_exempt
# def get_all_users(request):
#     if request.method == 'GET':
#         users = Users.objects.all()
#         serializer = BaseUsersSerializer(users, many=True)
#         return JsonResponse(serializer.data, safe=False)


class SendMessageView(APIView):
    # permission_classes = [IsAuthenticated]  # Add authentication and permissions

    def post(self, request):
        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
