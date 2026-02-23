from rest_framework import serializers
from .models import CustomUser, Ticket, StudentStar


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'role', 'identity_id', 'is_identity_bound']


class RegisterSerializer(serializers.ModelSerializer):
    # 1. 删除了所有的 required=True，变成可选

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'name', 'role', 'identity_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 2. 如果前端没传，给默认值
        role = validated_data.get('role', 'student')
        identity_id = validated_data.get('identity_id', None)

        # 3. 自动识别超管
        is_staff = (role == 'admin')
        is_superuser = (role == 'admin')

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            role=role,
            identity_id=identity_id,
            is_identity_bound=False, # 注册即绑定，防止前端逻辑死循环
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return user


class TicketSerializer(serializers.ModelSerializer):
    submitter_name = serializers.ReadOnlyField(source='submitter.name')
    # 强制只读，防止前端传错报 400
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['submitter', 'status', 'submitTime', 'updateTime']


class StudentStarSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStar
        fields = '__all__'
