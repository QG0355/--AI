from rest_framework import serializers
from .models import CustomUser, Ticket, OARequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'identity_id', 'is_identity_bound', 'extra_permissions']

class RegisterSerializer(serializers.ModelSerializer):
    # 确保这三个字段必填
    name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    identity_id = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'name', 'role', 'identity_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name'],
            role=validated_data['role'],           # 保存前端传来的角色
            identity_id=validated_data['identity_id'], # 保存前端传来的学号
            is_identity_bound=True                 # 注册即视为已绑定
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