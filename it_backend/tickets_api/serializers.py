from rest_framework import serializers
from .models import CustomUser, Ticket, TicketAttachment, ServiceStar


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'gender', 'avatar', 'role', 'identity_id', 'is_identity_bound']

    def get_avatar(self, obj):
        request = self.context.get('request')
        url = getattr(obj, 'avatar_display', '') or ''
        if request and url and not url.startswith('http'):
            url = request.build_absolute_uri(url)
        return url


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
    submitter_name = serializers.SerializerMethodField()
    # 强制只读，防止前端传错报 400
    status = serializers.CharField(read_only=True)
    rejected_reason = serializers.CharField(read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['submitter', 'status', 'submitTime', 'updateTime']

    def get_attachments(self, obj):
        request = self.context.get('request')
        items = []
        for a in obj.attachments.all().order_by('id'):
            url = a.file.url if a.file else ''
            if request and url and not url.startswith('http'):
                url = request.build_absolute_uri(url)
            items.append({
                'id': a.id,
                'media_type': a.media_type,
                'url': url,
                'original_name': a.original_name,
                'uploaded_at': a.uploaded_at
            })
        return items

    def get_submitter_name(self, obj):
        request = self.context.get('request')
        if not request:
            return getattr(obj.submitter, 'name', '') or getattr(obj.submitter, 'username', '') or ''
        viewer = getattr(request, 'user', None)
        if getattr(obj, 'is_anonymous', False) and getattr(obj, 'status', '') == 'closed':
            if viewer and getattr(viewer, 'role', None) == 'maintenance':
                return '匿名'
        return getattr(obj.submitter, 'name', '') or getattr(obj.submitter, 'username', '') or ''


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'media_type', 'file', 'original_name', 'uploaded_at']
        read_only_fields = ['id', 'ticket', 'media_type', 'original_name', 'uploaded_at']


class ServiceStarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStar
        fields = '__all__'
