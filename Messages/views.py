from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MessageItemInfo, MessageReceivers
from .serializers import CreateMessageSerializer, LoginSerializer, RetrieveDestroyOutputMessageSerializer, \
    MessageReceiverSerializer, MessageItemInfoExtendedSerializer, AllMessageItemInfoSerializer, \
    UnreadMessageItemInfoSerializer


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


class RetrieveMessageDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetrieveDestroyOutputMessageSerializer
    queryset = MessageItemInfo.objects.all()
    lookup_field = "message_id"

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


class DeleteMessageDetailsView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = "message_id"

    def get_serializer_class(self):
        sender = MessageItemInfo.objects.get(message_id=self.kwargs.get("message_id")).sender
        if sender == self.request.user.id:
            return MessageItemInfo
        return MessageReceiverSerializer

    def get_queryset(self):
        obj = MessageItemInfo.objects.get(message_id=self.kwargs.get("message_id"))
        print(obj.sender.id, self.request.user.id)
        if obj.sender.id == self.request.user.id:
            return MessageItemInfo.objects.all()
        return MessageReceivers.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Order deleted successfully"
        }, status=status.HTTP_200_OK)


class CreateListMessageView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MessageItemInfo.objects.all()
    serializer_class = AllMessageItemInfoSerializer

    def post(self, request):
        serializer = CreateMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            message_data = MessageItemInfoExtendedSerializer(message).data

            return Response(message_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user

        messages = MessageItemInfo.objects.filter(
            Q(sender=user) | Q(messagereceivers__receiver=user)).distinct()
        return messages


class ListUnreadMessageView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = UnreadMessageItemInfoSerializer

    def get_queryset(self):
        user = self.request.user

        messages = MessageItemInfo.objects.filter(
            Q(sender=user) | Q(messagereceivers__receiver=user)).distinct()
        return messages
