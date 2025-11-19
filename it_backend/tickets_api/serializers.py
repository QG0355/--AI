from rest_framework import serializers
from .models import CustomUser, Ticket, OARequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'identity_id', 'is_identity_bound', 'extra_permissions']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'name', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role='student'  # 注册默认都是学生，身份绑定时再改
        )
        return user


class TicketSerializer(serializers.ModelSerializer):
    submitter_name = serializers.ReadOnlyField(source='submitter.name')

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['submitter', 'status', 'submitTime', 'updateTime']


class OARequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.ReadOnlyField(source='requester.name')
    requester_role = serializers.ReadOnlyField(source='requester.role')

    class Meta:
        model = OARequest
        fields = '__all__'
        read_only_fields = ['requester', 'status', 'created_at']