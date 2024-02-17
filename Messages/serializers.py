# import serializer from rest_framework
from rest_framework import serializers

# import model from models.py
from .models import Users, MessageItemInfo, MessageReceivers


# Create a model serializer
class BaseUsersSerializer(serializers.ModelSerializer):
    # specify model and fields
    class Meta:
        model = Users
        fields = ['username']


class ExtendedUsersSerializer(BaseUsersSerializer):
    # specify model and fields
    class Meta:
        model = Users
        fields = '__all__'


# Create a model serializer
class MessageReceiversSerializer(serializers.HyperlinkedModelSerializer):
    # specify model and fields
    class Meta:
        model = MessageReceivers
        fields = ['message_id', 'receiver', 'read']


# Create a model serializer
class MessageItemInfoSerializer(serializers.ModelSerializer):
    sender = BaseUsersSerializer(read_only=True)
    receivers = serializers.SlugRelatedField(
        queryset=Users.objects.all(), slug_field='username', many=True)

    class Meta:
        model = MessageItemInfo
        fields = ['message_id', 'subject', 'text', 'date_created', 'sender', 'receivers']


class CreateMessageInfoSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=25)
    receivers = serializers.SlugRelatedField(
        queryset=Users.objects.all(), slug_field='username', many=True)
    subject = serializers.CharField(max_length=35)
    text = serializers.CharField()

    def validate(self, data):
        try:
            sender = data.get('sender')
            receivers = data.get('receivers')
            # print("sender", sender)
            # print("receivers", receivers)
        except Exception:
            raise serializers.ValidationError({'receivers and sender': 'Invalid username'})
        # Validate sender exists
        if not Users.objects.filter(username=sender).exists():
            raise serializers.ValidationError({'sender': 'Invalid sender username'})

        # Validate receivers exist
        for receiver in receivers:
            if not Users.objects.filter(username=receiver.username).exists():
                raise serializers.ValidationError({'receivers': 'Invalid receiver username'})

        return data

    def create(self, validated_data):
        sender_username = validated_data['sender']
        sender = Users.objects.get(username=sender_username)

        message_info = MessageItemInfo.objects.create(
            sender=sender,
            subject=validated_data['subject'],
            text=validated_data['text'],
        )

        # Create MessageReceivers instances after message_info is created
        receivers = []
        for receiver_obj in validated_data['receivers']:
            receiver = Users.objects.get(username=receiver_obj.username)
            receivers.append(MessageReceivers(message_id=message_info, receiver=receiver))

        # Bulk create MessageReceivers instances
        MessageReceivers.objects.bulk_create(receivers)
        return message_info

