from django.contrib.auth.models import User
from rest_framework import serializers

from Messages.models import MessageItemInfo, MessageReceivers


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id']


class CreateMessageSerializer(serializers.ModelSerializer):
    sender = serializers.IntegerField(default=serializers.CurrentUserDefault())
    receivers = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = MessageItemInfo
        fields = ("message_id", "sender", "receivers", "subject", "text", "dateCreated")
        validators = []

    #
    # def get_context(self):
    #     return {'request': self.context['request']}

    def validate_sender(self, value):

        print("Sender ID:", value)

        # Add this line to check existing user IDs
        print("Existing User IDs:", list(User.objects.values_list('id', flat=True)))

        try:
            sender = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender")
        if not value:
            value = self.context['request'].user.id

        elif value != self.context['request'].user.id:
            raise serializers.ValidationError("Sender must be logged in user")

        return value

    def validate_receivers(self, value):

        receiver_ids = value or []
        if len(receiver_ids) == 0:
            raise serializers.ValidationError(f"Receivers list is empty")
        # Validate receivers exist
        invalid_ids = []
        for receiver_id in receiver_ids:
            try:
                User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                invalid_ids.append(receiver_id)

        if invalid_ids:
            raise serializers.ValidationError(f"Invalid receiver IDs: {invalid_ids}")

        # # Validate against request user
        # if self.context['request'].user.id in receiver_ids:
        #     raise serializers.ValidationError("Cannot send to self")

        return receiver_ids

    def create(self, validated_data):

        sender_id = validated_data.get('sender') or self.context['request'].user.id

        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender")

        receivers_data = validated_data.pop('receivers')

        # Create message
        message = MessageItemInfo.objects.create(sender=sender, **validated_data)

        receiver_ids = [receiver_id for receiver_id in receivers_data]

        # Create relationships
        for receiver_id in receiver_ids:
            MessageReceivers.objects.create(
                message=message,
                receiver_id=receiver_id
            )

        return message


class RetrieveDestroyOutputMessageSerializer(serializers.ModelSerializer):
    receivers = serializers.SerializerMethodField()

    class Meta:
        model = MessageItemInfo
        fields = ("message_id", "sender", "receivers", "subject", "text", "dateCreated")
        validators = []

    def validate_sender(self, value):
        if not self.context['request'].resolver_match.kwargs['lookup_field']:
            if value != self.context['request'].user.id:
                raise serializers.ValidationError("You don't have permission to write message for someone else!")
        return value

    def create(self, validated_data):
        sender_username = validated_data.pop('sender')
        receiver_usernames = validated_data.pop('receivers')
        sender_instance = User.objects.get(username=sender_username)
        message = MessageItemInfo.objects.create(sender=sender_instance, **validated_data)

        for receiver_username in receiver_usernames:
            receiver_instance = User.objects.get(username=receiver_username)
            MessageReceivers.objects.create(message=message, receiver=receiver_instance, read=False)

        return message

    def get_receivers(self, obj):
        receivers = MessageReceivers.objects.filter(message=obj.message_id)
        return [receiver.receiver.id for receiver in receivers]


class MessageItemInfoSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receivers = serializers.SerializerMethodField()

    class Meta:
        model = MessageItemInfo
        fields = ('message_id', 'sender', 'receivers', 'subject', 'text', 'dateCreated')

    def get_receivers(self, obj):
        receivers = MessageReceivers.objects.filter(message=obj.message_id)
        return [receiver.receiver.username for receiver in receivers]


class MessageReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReceivers
        fields = ['message', 'receiver', 'read']
        validators = []
