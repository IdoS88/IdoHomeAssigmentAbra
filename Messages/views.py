# @csrf_exempt
# def get_all_users(request):
#     if request.method == 'GET':
#         users = Users.objects.all()
#         serializer = BaseUsersSerializer(users, many=True)
#         return JsonResponse(serializer.data, safe=False)


from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MessageItemInfo, MessageReceivers, Users
from .serializers import MessageSerializer


class CreateMessageView(APIView):

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Save message
            messageEntity = MessageItemInfo.objects.create(
                sender_id=Users.objects.get(username=serializer.validated_data['sender']).username,
                subject=serializer.validated_data['subject'],
                text=serializer.validated_data['text']
            )

            # Save receivers
            for receiver in serializer.validated_data['receivers']:
                MessageReceivers.objects.create(
                    message_id=messageEntity.message,
                    receiver_id=Users.objects.get(username=receiver).username
                )

            return Response({
                "message": "Message created successfully",
                "message_id": messageEntity.message
            }, status=201)

        else:
            return Response(serializer.errors, status=400)
