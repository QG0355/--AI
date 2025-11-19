from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import CustomUser, Ticket, OARequest
from .serializers import UserSerializer, RegisterSerializer, TicketSerializer, OARequestSerializer


# 1. 登录
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


# 2. 注册
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 3. 身份绑定 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_identity(request):
    user = request.user
    if user.is_identity_bound:
        return Response({"detail": "您已经绑定过身份，无法修改！"}, status=400)

    role = request.data.get('role')
    identity_id = request.data.get('identity_id')
    name = request.data.get('name')

    if not all([role, identity_id, name]):
        return Response({"detail": "请填写完整信息"}, status=400)

    # 更新用户信息
    user.role = role
    user.identity_id = identity_id
    user.name = name
    user.is_identity_bound = True
    user.save()

    return Response({"detail": "绑定成功", "user": UserSerializer(user).data})


# 4. 报修单 API
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 简单逻辑：大家都能看自己的，管理员看所有
        if self.request.user.role == 'admin':
            return Ticket.objects.all()
        return Ticket.objects.filter(submitter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(submitter=self.request.user)


# 5. OA 审批 API
class OAViewSet(viewsets.ModelViewSet):
    serializer_class = OARequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 老师看待老师审批的，管理员看待管理员审批的，学生看自己的
        if user.role == 'admin':
            return OARequest.objects.filter(status='pending_admin')
        elif user.role == 'teacher':
            return OARequest.objects.filter(status='pending_teacher')
        else:
            return OARequest.objects.filter(requester=user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


# 6. OA 审批动作 (同意/拒绝)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_oa(request, pk):
    try:
        oa = OARequest.objects.get(pk=pk)
    except OARequest.DoesNotExist:
        return Response(status=404)

    action = request.data.get('action')  # 'approve' or 'reject'
    user = request.user

    if action == 'reject':
        oa.status = 'rejected'
        oa.save()
        return Response({"detail": "已拒绝"})

    if action == 'approve':
        if user.role == 'teacher' and oa.status == 'pending_teacher':
            oa.status = 'pending_admin'  # 转交管理员
            oa.save()
            return Response({"detail": "已同意，转交管理员审批"})

        elif user.role == 'admin' and oa.status == 'pending_admin':
            oa.status = 'approved'
            oa.save()

            # 关键：给申请人添加权限
            requester = oa.requester
            # 这里的逻辑是把申请的区域加到 extra_permissions 列表里
            perms = requester.extra_permissions
            if oa.target_area not in perms:
                perms.append(oa.target_area)
                requester.extra_permissions = perms
                requester.save()

            return Response({"detail": "审批通过，权限已开通"})

    return Response({"detail": "无权操作"}, status=403)