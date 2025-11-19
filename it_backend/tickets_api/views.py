from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import CustomUser, Ticket, OARequest
from .serializers import UserSerializer, RegisterSerializer, TicketSerializer, OARequestSerializer

from rest_framework.decorators import action
from django.db.models import Q

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
        user = self.request.user

        # 1. 学生：只能看自己提交的
        if user.role == 'student':
            return Ticket.objects.filter(submitter=user)

        # 2. 宿管：看自己提交的 + 待宿管审核的(pending_dorm)
        elif user.role == 'dorm_manager':
            return Ticket.objects.filter(Q(submitter=user) | Q(status='pending_dorm'))

        # 3. 报修管理员：看所有 + 待派单的(pending_dispatch)
        elif user.role == 'repair_admin' or user.role == 'admin':
            return Ticket.objects.all()

        # 4. 维修人员：看自己提交的 + 指派给自己的
        elif user.role == 'maintenance':
            return Ticket.objects.filter(Q(submitter=user) | Q(assignee=user))

        # 5. 老师/教学楼管理员：目前只能看自己提交的
        else:
            return Ticket.objects.filter(submitter=user)

    def perform_create(self, serializer):
        user = self.request.user
        # 初始状态逻辑：
        # 如果是学生 -> 状态设为 'pending_dorm' (待宿管审)
        # 如果是老师/宿管/管理员 -> 状态设为 'pending_dispatch' (直接待派单)
        initial_status = 'pending_dispatch'
        if user.role == 'student':
            initial_status = 'pending_dorm'

        serializer.save(submitter=user, status=initial_status)

    # 增加一个动作：处理工单 (审核/派单/完成/评价)
    # URL: /api/tickets/<id>/handle/
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        ticket = self.get_object()
        user = request.user
        action_type = request.data.get('type')  # approve, assign, finish, evaluate

        # 1. 宿管审核 (学生提交的单子)
        if action_type == 'approve_dorm' and user.role == 'dorm_manager':
            ticket.status = 'pending_dispatch'  # 转给报修管理员
            ticket.save()
            return Response({'status': '审核通过，已转交报修管理员'})

        # 2. 报修管理员派单
        if action_type == 'assign' and user.role in ['repair_admin', 'admin']:
            worker_id = request.data.get('worker_id')
            try:
                worker = CustomUser.objects.get(pk=worker_id, role='maintenance')
                ticket.assignee = worker
                ticket.status = 'repairing'
                ticket.save()
                return Response({'status': f'已指派给 {worker.name}'})
            except CustomUser.DoesNotExist:
                return Response({'error': '维修人员不存在'}, status=400)

        # 3. 报修管理员/宿管 驳回 (认为是瞎报修)
        if action_type == 'reject' and user.role in ['repair_admin', 'admin', 'dorm_manager']:
            ticket.status = 'rejected'
            ticket.save()
            return Response({'status': '已驳回'})

        # 4. 维修人员完成维修
        if action_type == 'finish' and user.role == 'maintenance':
            ticket.status = 'finished'
            ticket.save()
            return Response({'status': '维修完成，等待学生评价'})

        # 5. 学生评价
        if action_type == 'evaluate' and user == ticket.submitter:
            ticket.evaluation = request.data.get('comment')
            ticket.rating = request.data.get('rating', 5)
            ticket.status = 'closed'
            ticket.save()
            return Response({'status': '评价成功，工单结束'})

        return Response({'error': '无权操作或状态不正确'}, status=403)


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