from rest_framework import serializers

from .models import Users, MessageItemInfo, MessageReceivers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('username',)
        validators = []


from rest_framework import serializers
from .models import Users, MessageItemInfo, MessageReceivers


class MessageSerializer(serializers.Serializer):
    sender = serializers.CharField()
    subject = serializers.CharField()
    text = serializers.CharField()
    receivers = serializers.ListField(child=serializers.CharField())

    def validate(self, data):
        # Validate sender exists
        try:
            Users.objects.get(username=data['sender'])
        except Users.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist")

        # Validate all receivers exist
        for receiver in data['receivers']:
            try:
                Users.objects.get(username=receiver)
            except Users.DoesNotExist:
                raise serializers.ValidationError(f"Receiver {receiver} does not exist")

        return data

class MessageReceiverSerializer(serializers.ModelSerializer):
    receiver = UserSerializer()

    class Meta:
        model = MessageReceivers
        fields = ('message', 'receiver', 'read')


class CreateMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(required=True)
    receivers = UserSerializer(many=True, required=True)

    class Meta:
        model = MessageItemInfo
        fields = ("message", "sender", "receivers", "subject", "text", "dateCreated")
        validators = []

    def create(self, validated_data):
        sender_data = validated_data.pop('sender')
        sender_username = sender_data['username']

        receivers_data = validated_data.pop('receivers', [])
        receivers_usernames = [receiver['username'] for receiver in receivers_data]

        # Check if sender exists
        try:
            sender_instance = Users.objects.get(username=sender_username)
        except Users.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")

        # Check if all receivers exist
        existing_receivers = Users.objects.filter(username__in=receivers_usernames)
        if existing_receivers.count() != len(receivers_usernames):
            raise serializers.ValidationError("One or more receiver users do not exist.")

        # Create MessageItemInfo instance
        message_item_info = MessageItemInfo.objects.create(sender=sender_instance, **validated_data)
        return message_item_info
