from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Users, MessageItemInfo, MessageReceivers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('username',)


class MessageItemInfoSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = MessageItemInfo
        fields = ('message_id', 'sender', 'subject', 'text', 'date_created')


class MessageReceiverSerializer(serializers.ModelSerializer):
    receiver = UserSerializer()

    class Meta:
        model = MessageReceivers
        fields = ('message_id', 'receiver', 'read')


class CreateMessageSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=25)
    receivers = serializers.ListField(child=serializers.CharField(max_length=25))
    subject = serializers.CharField(max_length=35)
    text = serializers.CharField()

    def validate_sender(self, value):
        try:
            user = Users.objects.get(username=value)
        except Users.DoesNotExist:
            raise ValidationError("Sender does not exist.")
        return user

    def validate_receivers(self, value):
        users = []
        for username in value:
            try:
                user = Users.objects.get(username=username)
            except Users.DoesNotExist:
                raise ValidationError(f"Receiver '{username}' does not exist.")
            users.append(user)
        return users

    def create(self, validated_data):
        message = self.create_message(validated_data)
        self.create_receivers(message, validated_data)
        return message

    def create_message(self, validated_data):
        message_fields = {
            field: value
            for field, value in validated_data.items()
            if field in MessageItemInfo._meta.fields
        }

        return MessageItemInfo.objects.create(**message_fields)

        def create_receivers(self, message, validated_data):
            receivers = validated_data['receivers']

            for receiver in receivers:
                MessageReceivers.objects.create(
                    message_id=message,
                    receiver=receiver
                )
