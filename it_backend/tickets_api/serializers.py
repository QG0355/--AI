from rest_framework import serializers
from .models import CustomUser, Ticket, OARequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'identity_id', 'is_identity_bound', 'extra_permissions']

class RegisterSerializer(serializers.ModelSerializer):
    # 注册只需要这三个字段
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 创建一个“空白”用户：没有名字，没有角色，没有身份ID，未绑定
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name='',             # 暂时为空
            role='student',      # 默认先给个学生角色，绑定时再改
            identity_id=None,    # 暂时为空
            is_identity_bound=False # 关键！标记为未绑定
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