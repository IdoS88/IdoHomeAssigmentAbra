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
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")
        return value

    def validate_receivers(self, value):
        for username in value:
            try:
                User.objects.get(id=username)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"Receiver '{username}' does not exist.")
        return value

    def create(self, validated_data):
        sender_id = validated_data.pop('sender')
        receiver_ids = validated_data.pop('receivers')
        sender_instance = User.objects.get(id=sender_id)
        message = MessageItemInfo.objects.create(sender=sender_instance, **validated_data)

        for receiver_username in receiver_ids:
            receiver_instance = User.objects.get(id=receiver_username)
            MessageReceivers.objects.create(message=message, receiver=receiver_instance, read=False)

        return message

    def get_receivers(self, obj):
        receivers = MessageReceivers.objects.filter(message=obj.message_id)
        return [receiver.receiver.id for receiver in receivers]


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
    class Meta:
        model = MessageItemInfo
        fields = ('message_id', 'sender', 'subject', 'text', 'dateCreated')


class MessageReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReceivers
        fields = ['message', 'receiver', 'read']
        validators = []


class MessageItemInfoExtendedSerializer(MessageItemInfoSerializer):
    receivers = serializers.SerializerMethodField()

    class Meta:
        model = MessageItemInfo
        fields = ('message_id', 'sender', 'receivers', 'subject', 'text', 'dateCreated')

    def get_receivers(self, obj):
        receivers = MessageReceivers.objects.filter(message=obj.message_id)
        return [receiver.receiver.id for receiver in receivers]


class AllMessageItemInfoSerializer(serializers.ModelSerializer):
    receivers = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    class Meta:
        model = MessageItemInfo
        fields = ['message_id', 'sender', 'subject', 'text', 'dateCreated', 'receivers', 'read']

    def get_receivers(self, obj):
        user = self.context['request'].user

        return MessageReceivers.objects.filter(message=obj.message_id, receiver=user.id).values_list('receiver',
                                                                                                     flat=True)

    def get_read(self, obj):
        user = self.context['request'].user
        read = MessageReceivers.objects.filter(message=obj.message_id, receiver=user.id).values_list('read',
                                                                                                     flat=True).first()
        return read


class UnreadMessageItemInfoSerializer(AllMessageItemInfoSerializer):
    def get_read(self, obj):
        readMessage = MessageReceivers.objects.filter(receiver=self.context['request'].user.id, read=False)
        return (receiver.read
                for receiver in readMessage)
