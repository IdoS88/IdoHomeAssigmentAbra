# @csrf_exempt
# def get_all_users(request):
#     if request.method == 'GET':
#         users = Users.objects.all()
#         serializer = BaseUsersSerializer(users, many=True)
#         return JsonResponse(serializer.data, safe=False)
import json
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MessageItemInfo, MessageReceivers
from .serializers import MessageSerializer, MessageReceiverSerializer, LoginSerializer


class LoginAPIView(APIView):
    """This api will handle login and return token for authenticate user."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                """We are reterving the token for authenticated user."""
                token = Token.objects.get(user=user)
                response = {
                    "status": status.HTTP_200_OK,
                    "message": "success",
                    "data": {
                        "Token": token.key
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid Email or Password",
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        response = {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "bad request",
            "data": serializer.errors
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


def updateToRead(message_id):
    model_to_patch = MessageReceivers.objects.get(message_id=message_id)
    serializer = MessageReceiverSerializer(model_to_patch, data=json.dumps({"read": True}),
                                           partial=True)  # set partial=True to update a data partially
    if serializer.is_valid():
        serializer.save()
        print(serializer.data)
        return True
    return False


class MessageDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, message_id):
        if not isinstance(message_id, uuid.UUID):
            return Response("Invalid message ID", status=400)

        try:
            message = MessageItemInfo.objects.get(id=message_id)
        except MessageItemInfo.DoesNotExist:
            return Response("Message not found", status=404)

        try:
            receivers = []
            receiver_qs = MessageReceivers.objects.filter(message=message_id)
            for receiver_row in receiver_qs:
                user = receiver_row.receiver.username
                receivers.append(user)

            data = {
                "message_id": message.id,
                "sender": message.sender.username,
                "receivers": receivers,
                "subject": message.subject,
                "text": message.text,
                "dateCreated": message.dateCreated
            }
            # Check if the user is the sender or one of the receivers
            if self.request.user.id != message.sender.username and self.request.user.username not in receivers:
                return Response("You don't have permission to view this message", status=403)
            if any(value == "" or value is None for value in data.values()):
                raise Exception("Receivers not Found")
        except Exception as e:
            return Response(data={"errors": e}, status=404)
        if not updateToRead(message_id):
            # TODO : error message to add
            return JsonResponse(status=400)

        return JsonResponse(data, status=200)


class CreateMessageView(APIView):

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data["sender"] != self.request.auth.key:
                return Response("You don't have permission to write this message from this sender", status=403)
            # Save message
            messageEntity = MessageItemInfo.objects.create(
                sender_id=User.objects.get(username=serializer.validated_data['sender']).username,
                subject=serializer.validated_data['subject'],
                text=serializer.validated_data['text']
            )

            # Save receivers
            for receiver in serializer.validated_data['receivers']:
                MessageReceivers.objects.create(
                    message_id=messageEntity.id,
                    receiver_id=User.objects.get(username=receiver).username
                )

            return Response({
                "details": "Message created successfully",
                "message_id": messageEntity.id
            }, status=201)

        else:
            return Response(serializer.errors, status=400)
