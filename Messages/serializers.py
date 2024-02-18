from rest_framework import serializers

from .models import Users, MessageItemInfo, MessageReceivers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('username',)
        validators = []


class MessageItemInfoSerializer(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = MessageItemInfo
        fields = ('message', 'sender', 'subject', 'text', 'dateCreated')


class MessageReceiverSerializer(serializers.ModelSerializer):
    receiver = UserSerializer()

    class Meta:
        model = MessageReceivers
        fields = ('message', 'receiver', 'read')


class CreateMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(required=True)

    class Meta:
        model = MessageItemInfo
        fields = ("message", "sender", "subject", "text", "dateCreated")
        validators = []

    # def validate_sender(self, value):
    #     """
    #     Validate the sender user.
    #     """
    #     user_data = value
    #
    #     # Assuming you have a unique field in your Users model (e.g., 'username')
    #     username = user_data.get('username')
    #
    #     if not Users.objects.filter(username=username).exists():
    #         raise serializers.ValidationError("Sender user does not exist.")
    #
    #     return user_data

    def create(self, validated_data):
        sender_data = validated_data.pop('sender')
        username = sender_data['username']

        # Check if user already exists
        try:
            user_instance = Users.objects.get(username=username)
        except Users.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")

        # Create MessageItemInfo instance
        message_item_info = MessageItemInfo.objects.create(sender=user_instance, **validated_data)
        return message_item_info

    # def validate_receivers(self, value):
    #     users = []
    #     for username in value:
    #         try:
    #             user = Users.objects.get(username=username)
    #         except Users.DoesNotExist:
    #             raise ValidationError(f"Receiver '{username}' does not exist.")
    #         users.append(user)
    #     return users
    # def create_message(self, validated_data):
    #     message_fields = {
    #         field: value
    #         for field, value in validated_data.items()
    #         if field in MessageItemInfo._meta.fields
    #     }
    #
    #     return MessageItemInfo.objects.create(**message_fields)

    # def create_receivers(self, message, validated_data):
    #     receivers = validated_data['receivers']
    #     receivers_entities = []
    #     for receiver in receivers:
    #         receivers_entities += MessageReceivers.objects.create(
    #             message_id=message,
    #             receiver=receiver
    #         )
    #     return receivers_entities
