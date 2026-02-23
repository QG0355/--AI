from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, StudentStar, StudentProfile, MaintenanceProfile, AuditorProfile
from rest_framework import filters

from .models import CustomUser, Ticket
from .serializers import UserSerializer, RegisterSerializer, TicketSerializer, StudentStarSerializer


# 1. Login View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


# 2. Register View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 3. Identity Bind View (Kept to prevent 404s from frontend, though logic is simplified)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_identity(request):
    user = request.user
    if user.is_identity_bound:
        return Response({"detail": "您已经绑定过身份，无需重复操作", "user": UserSerializer(user).data}, status=200)

    role = request.data.get('role')
    identity_id = request.data.get('identity_id')
    user.role = role
    user.identity_id = identity_id
    user.name = request.data.get('name')
    user.is_identity_bound = True
    user.save()

    if role == 'student':
        StudentProfile.objects.update_or_create(user=user, defaults={'student_id': identity_id})
    elif role == 'maintenance':
        MaintenanceProfile.objects.update_or_create(user=user, defaults={'worker_id': identity_id})
    elif role in ['auditor', 'admin']:
        AuditorProfile.objects.update_or_create(user=user, defaults={'auditor_id': identity_id})

    return Response({"detail": "Bind successful", "user": UserSerializer(user).data})


# 4. Ticket ViewSet
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'id']
    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.all()
        # Admin 和 审核员 作为审核 / 管理角色，看到全部工单
        if user.role in ['admin', 'auditor']:
            pass
        # 维修人员看到所有工单，便于抢单
        elif user.role == 'maintenance':
            pass
        # 其他角色只看到自己提交的工单
        else:
            qs = qs.filter(submitter=user)

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        # 新建工单默认进入“待审核员审核”状态
        serializer.save(submitter=self.request.user, status='pending_dorm')

    # Ticket Handling Action (Assign, Finish, Evaluate)
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        ticket = self.get_object()
        action_type = request.data.get('type')

        # Dispatch (Assign)
        if action_type == 'assign':
            worker_id = request.data.get('worker_id')
            try:
                worker = CustomUser.objects.get(pk=worker_id)
                ticket.assignee = worker
                ticket.status = 'repairing'
                ticket.save()
                return Response({'status': 'Dispatched'})
            except CustomUser.DoesNotExist:
                return Response({'error': 'Worker not found'}, status=400)

        # Finish Repair
        if action_type == 'finish':
            ticket.status = 'finished'
            ticket.save()
            return Response({'status': 'Repair Finished'})


        return Response({'error': 'Unknown action'}, status=400)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        ticket = self.get_object()
        user = request.user
        if user.role not in ['admin', 'auditor']:
            return Response({'detail': '无权限执行审核操作'}, status=status.HTTP_403_FORBIDDEN)

        decision = request.data.get('decision')
        if decision == 'approve':
            ticket.status = 'pending_dispatch'
            ticket.save()
            return Response({'status': 'Approved'})
        if decision == 'reject':
            ticket.status = 'rejected'
            ticket.save()
            return Response({'status': 'Rejected'})

        return Response({'detail': '未知操作'}, status=status.HTTP_400_BAD_REQUEST)


class StudentStarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentStar.objects.filter(is_active=True).order_by('sort_order', '-id')
    serializer_class = StudentStarSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    user = request.user
    content = request.data.get('message', '').strip()
    if not content:
        return Response({"detail": "问题内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)
    reply = f"您好，{user.name or user.username}。根据您提供的描述“{content}”，建议您先确认设备电源、线路和使用环境是否正常，如有安全隐患请第一时间联系现场老师或后勤老师进行处理。AI 对话仅供参考，请以学校实际报修流程和专业维修人员意见为准，不能盲目相信。"
    return Response({"reply": reply})


def change_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 简单的状态流转逻辑
    if order.status == 0:  # 待接单 -> 维修中
        order.status = 1
    elif order.status == 1:  # 维修中 -> 已完成
        order.status = 2

    order.save()

    # 关键修改：返回 JSON 给 Vue，告诉它最新的状态是多少
    return JsonResponse({
        'code': 200,
        'msg': '状态更新成功',
        'new_status': order.status
    })
