# @csrf_exempt
# def get_all_users(request):
#     if request.method == 'GET':
#         users = Users.objects.all()
#         serializer = BaseUsersSerializer(users, many=True)
#         return JsonResponse(serializer.data, safe=False)
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MessageItemInfo, MessageReceivers
from .serializers import CreateMessageSerializer, LoginSerializer, RetrieveDestroyOutputMessageSerializer


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


# class MessagePermissionMixin():
#     permission_classes = [IsAuthenticated]
#     model = MessageItemInfo
#
#     def get_object(self):
#         try:
#             message = super().get_object()
#             if self.request.user.id != message.sender and self.request.user.id not in message.receivers:
#                 raise NotFound("You don't have permission to view this message")
#             return message
#         except MessageItemInfo.DoesNotExist:
#             raise NotFound("Message not found")
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update({'request': self.request})
#         return context

# PermissionRequiredMixin
class RetrieveMessageDetailsView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetrieveDestroyOutputMessageSerializer
    queryset = MessageItemInfo.objects.all()
    lookup_field = "message_id"

    # permission_required = ["messages.view_MessageItemInfo", "messages.change_MessageReceivers"]

    def get(self, request, *args, **kwargs):
        get = self.retrieve(request, *args, **kwargs)
        try:
            receiver = MessageReceivers.objects.get(message_id=self.kwargs.get("message_id"),
                                                    receiver=self.request.user.id)
            receiver.read = True
            receiver.save()
        except MessageReceivers.DoesNotExist as e:
            if self.request.user.id != get.data.sender:
                Response(e, status=status.HTTP_403_FORBIDDEN)
        return get
    def get_queryset(self):
        if()


class DeleteMessageDetailsView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]




class ListCreateMessageView(LoginRequiredMixin, generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = MessageItemInfo.objects.all()
    serializer_class = CreateMessageSerializer

    # return MessageItemInfo.objects.filter(message_id=self.lookup_field) for list
    def post(self, request):
        serializer = CreateMessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Save message
            messageEntity = MessageItemInfo.objects.create(
                sender_id=request.user.id,
                subject=serializer.validated_data['subject'],
                text=serializer.validated_data['text']
            )

            # Save receivers
            for receiver in serializer.validated_data['receivers']:
                MessageReceivers.objects.create(
                    message_id=messageEntity.message_id,
                    receiver_id=User.objects.get(id=receiver).id
                )

            return Response({
                "details": "Message created successfully",
                "message_id": messageEntity.message_id
            }, status=201)

        else:
            return Response(serializer.errors, status=400)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self):
        print(MessageItemInfo.objects.filter(sender=self.request.user.id))
        # serializer = MessageSerializer()
