from django.contrib.auth.models import User
from rest_framework import serializers

from .models import MessageItemInfo, MessageReceivers


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class MessageSerializer(serializers.Serializer):
    sender = serializers.CharField()
    subject = serializers.CharField()
    text = serializers.CharField()
    receivers = serializers.ListField(child=serializers.CharField())

    def validate(self, data):
        # Validate sender exists
        try:
            User.objects.get(username=data['sender'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist")

        # Validate all receivers exist
        for receiver in data['receivers']:
            try:
                User.objects.get(username=receiver)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"Receiver {receiver} does not exist")

        return data


class MessageReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReceivers
        fields = ('message', 'receiver', 'read')
        validators = []


class CreateMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.username")
    receivers = serializers.ListField(child=serializers.CharField(), source="receivers")

    class Meta:
        model = MessageItemInfo
        fields = ("message", "sender", "receivers", "subject", "text", "dateCreated")
        validators = []

    def create(self, validated_data):
        sender_data = validated_data.pop('sender')
        sender_id = sender_data['id']

        receivers_data = validated_data.pop('receivers', [])
        receivers_usernames = [receiver['username'] for receiver in receivers_data]

        # Check if sender exists
        try:
            sender_instance = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")

        # Check if all receivers exist
        existing_receivers = User.objects.filter(username__in=receivers_usernames)
        if existing_receivers.count() != len(receivers_usernames):
            raise serializers.ValidationError("One or more receiver users do not exist.")

        # Create MessageItemInfo instance
        message_item_info = MessageItemInfo.objects.create(sender=sender_instance, **validated_data)
        return message_item_info
