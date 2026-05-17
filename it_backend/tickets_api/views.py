from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action, parser_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Avg, Count
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import ServiceStar, StudentProfile, MaintenanceProfile, AuditorProfile, AiSetting, AiChatLog
from rest_framework import filters
import os
import json
import re
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .models import CustomUser, Ticket
from .serializers import UserSerializer, RegisterSerializer, TicketSerializer, ServiceStarSerializer
from .models import TicketAttachment


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    if request.method == 'PATCH':
        updates = {}
        if 'name' in request.data:
            name = (request.data.get('name') or '').strip()
            if not name:
                return Response({"detail": "姓名不能为空"}, status=status.HTTP_400_BAD_REQUEST)
            updates['name'] = name
        if 'gender' in request.data:
            gender = (request.data.get('gender') or '').strip()
            if gender not in {'unknown', 'male', 'female'}:
                return Response({"detail": "性别不合法"}, status=status.HTTP_400_BAD_REQUEST)
            updates['gender'] = gender

        if not updates:
            return Response({"detail": "没有可更新的字段"}, status=status.HTTP_400_BAD_REQUEST)

        for k, v in updates.items():
            setattr(user, k, v)
        user.save(update_fields=list(updates.keys()))
    data = UserSerializer(user, context={'request': request}).data
    if getattr(user, 'role', None) == 'maintenance':
        agg = Ticket.objects.filter(assignee=user, status='closed').aggregate(avg=Avg('rating'), cnt=Count('id'))
        avg = agg.get('avg')
        data['maintenance_rating'] = float(avg) if avg is not None else None
        data['maintenance_rating_count'] = int(agg.get('cnt') or 0)
    return Response(data)


# 1. Login View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user, context={'request': request}).data})


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
        return Response({"detail": "您已经绑定过身份，无需重复操作", "user": UserSerializer(user, context={'request': request}).data}, status=200)

    role = (request.data.get('role') or '').strip()
    identity_id = (request.data.get('identity_id') or '').strip()
    name = (request.data.get('name') or '').strip()

    if role not in {'student', 'maintenance', 'auditor', 'admin'}:
        return Response({"detail": "角色不合法"}, status=status.HTTP_400_BAD_REQUEST)
    if not identity_id:
        return Response({"detail": "工号/学号不能为空"}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(identity_id=identity_id).exclude(pk=user.pk).exists():
        return Response({"detail": "该工号/学号已被绑定，请确认后重试"}, status=status.HTTP_400_BAD_REQUEST)

    user.role = role
    user.identity_id = identity_id
    user.name = name
    user.is_identity_bound = True
    try:
        user.save()
    except IntegrityError:
        return Response({"detail": "该工号/学号已被绑定，请确认后重试"}, status=status.HTTP_400_BAD_REQUEST)

    if role == 'student':
        StudentProfile.objects.update_or_create(user=user, defaults={'student_id': identity_id})
    elif role == 'maintenance':
        MaintenanceProfile.objects.update_or_create(user=user, defaults={'worker_id': identity_id})
    elif role in ['auditor', 'admin']:
        AuditorProfile.objects.update_or_create(user=user, defaults={'auditor_id': identity_id})

    return Response({"detail": "Bind successful", "user": UserSerializer(user, context={'request': request}).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_my_avatar(request):
    user = request.user
    f = request.FILES.get('file') or request.FILES.get('avatar')
    if not f:
        return Response({"detail": "请上传头像文件(file)"}, status=status.HTTP_400_BAD_REQUEST)

    content_type = (getattr(f, 'content_type', '') or '').lower()
    allowed_types = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    if content_type and content_type not in allowed_types:
        return Response({"detail": "仅支持 JPG/PNG/WEBP/GIF 图片"}, status=status.HTTP_400_BAD_REQUEST)

    if f.size and f.size > 5 * 1024 * 1024:
        return Response({"detail": "图片大小不能超过 5MB"}, status=status.HTTP_400_BAD_REQUEST)

    old_name = getattr(getattr(user, 'avatar', None), 'name', '') or ''
    user.avatar = f
    user.avatar_url = ''
    user.save(update_fields=['avatar', 'avatar_url'])

    if old_name and old_name != getattr(user.avatar, 'name', ''):
        try:
            user.avatar.storage.delete(old_name)
        except Exception:
            pass

    return Response(UserSerializer(user, context={'request': request}).data)


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

    def perform_update(self, serializer):
        ticket = self.get_object()
        user = self.request.user
        if user.role == 'student':
            if ticket.submitter != user:
                raise PermissionDenied('只能修改自己提交的工单')
            if ticket.status != 'rejected':
                raise PermissionDenied('仅可修改被驳回的工单')
            serializer.save(status='pending_dorm', rejected_reason=None)
            return
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = request.user

        if user.role == 'student':
            if ticket.submitter != user:
                return Response({'detail': '只能撤销自己提交的工单'}, status=status.HTTP_403_FORBIDDEN)
            if ticket.status not in ['pending_dorm', 'pending_dispatch', 'rejected']:
                return Response({'detail': '当前状态不可撤销'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.role in ['admin', 'auditor']:
            pass
        else:
            return Response({'detail': '无权撤销工单'}, status=status.HTTP_403_FORBIDDEN)

        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Ticket Handling Action (Assign, Finish, Evaluate)
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        ticket = self.get_object()
        user = request.user
        action_type = request.data.get('type')

        # 权限控制：学生不能接单、派单、或完成维修
        if user.role == 'student':
            # 学生只能做“评价”或“取消工单”（如果允许的话），不能做 assign/finish
            # 这里先全部拦截，只允许后续加 evaluate
            if action_type in ['assign', 'finish', 'dispatch']:
                return Response({'detail': '学生无权执行此操作'}, status=status.HTTP_403_FORBIDDEN)

        # Dispatch (Assign)
        if action_type == 'assign':
            # 只有管理员、审核员可以派单；维修工可以抢单（如果允许自己给自己派）
            if user.role not in ['admin', 'auditor', 'maintenance']:
                 return Response({'detail': '无权派单'}, status=status.HTTP_403_FORBIDDEN)
            
            worker_id = request.data.get('worker_id')
            # 如果是维修工抢单，worker_id 应该是自己
            if user.role == 'maintenance':
                worker_id = user.id

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
            # 只有维修工（且是当前工单的处理人）或管理员可以点击完成
            if user.role == 'maintenance' and ticket.assignee != user:
                return Response({'detail': '只能完成指派给自己的工单'}, status=status.HTTP_403_FORBIDDEN)
            
            if user.role not in ['admin', 'maintenance']:
                return Response({'detail': '无权完成工单'}, status=status.HTTP_403_FORBIDDEN)

            ticket.status = 'finished'
            ticket.save()
            return Response({'status': 'Repair Finished'})

        if action_type == 'evaluate':
            if user.role != 'student':
                return Response({'detail': '无权评价工单'}, status=status.HTTP_403_FORBIDDEN)
            if ticket.submitter != user:
                return Response({'detail': '只能评价自己提交的工单'}, status=status.HTTP_403_FORBIDDEN)
            if ticket.status != 'finished':
                return Response({'detail': '当前状态不可评价'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                rating = int(request.data.get('rating') or 5)
            except Exception:
                return Response({'detail': '评分格式错误'}, status=status.HTTP_400_BAD_REQUEST)
            if rating < 1 or rating > 5:
                return Response({'detail': '评分需为 1-5'}, status=status.HTTP_400_BAD_REQUEST)

            evaluation = (request.data.get('evaluation') or '').strip()
            is_anonymous = bool(request.data.get('is_anonymous') or False)
            ticket.rating = rating
            ticket.evaluation = evaluation
            ticket.is_anonymous = is_anonymous
            ticket.status = 'closed'
            ticket.save()
            return Response({'status': 'Closed'})

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
            ticket.rejected_reason = None
            ticket.auditor = user  # 记录审核员
            ticket.save()
            return Response({'status': 'Approved'})
        if decision == 'reject':
            ticket.status = 'rejected'
            ticket.rejected_reason = (request.data.get('reason') or '').strip() or None
            ticket.auditor = user  # 记录审核员
            ticket.save()
            return Response({'status': 'Rejected'})

        return Response({'detail': '未知操作'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'], url_path='attachments', parser_classes=[MultiPartParser, FormParser])
    def attachments(self, request, pk=None):
        import os
        import imghdr

        ticket = self.get_object()
        user = request.user

        if request.method == 'GET':
            serializer = TicketSerializer(ticket, context={'request': request})
            return Response(serializer.data.get('attachments', []))
        
        # 多文件上传走 multipart/form-data
        # 在 DRF 中 parser 由 ViewSet 的 parser_classes 决定；这里按需懒加载处理

        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': '缺少文件 file'}, status=status.HTTP_400_BAD_REQUEST)

        if user.role == 'student' and ticket.submitter != user:
            return Response({'detail': '无权上传附件'}, status=status.HTTP_403_FORBIDDEN)
        if user.role not in ['student', 'admin', 'auditor']:
            return Response({'detail': '无权上传附件'}, status=status.HTTP_403_FORBIDDEN)
        if user.role == 'student' and ticket.status not in ['pending_dorm', 'rejected']:
            return Response({'detail': '当前状态不可上传附件'}, status=status.HTTP_400_BAD_REQUEST)
        if ticket.attachments.count() >= 6:
            return Response({'detail': '附件数量已达上限'}, status=status.HTTP_400_BAD_REQUEST)

        max_image = 5 * 1024 * 1024
        max_video = 50 * 1024 * 1024
        name = upload.name or ''
        ext = os.path.splitext(name)[1].lower()
        ct = (getattr(upload, 'content_type', '') or '').lower()

        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        video_exts = {'.mp4', '.webm', '.ogg', '.mov'}
        image_cts = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        video_cts = {'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime'}

        is_image = ext in image_exts and ct in image_cts
        is_video = ext in video_exts and (ct in video_cts or ct.startswith('video/'))

        if not (is_image or is_video):
            return Response({'detail': '仅支持图片(jpg/jpeg/png/gif/webp)与视频(mp4/webm/ogg/mov)'}, status=status.HTTP_400_BAD_REQUEST)

        if is_image and upload.size > max_image:
            return Response({'detail': '图片大小不能超过 5MB'}, status=status.HTTP_400_BAD_REQUEST)
        if is_video and upload.size > max_video:
            return Response({'detail': '视频大小不能超过 50MB'}, status=status.HTTP_400_BAD_REQUEST)

        if is_image:
            head = upload.read(2048)
            upload.seek(0)
            kind = imghdr.what(None, h=head)
            if kind not in {'jpeg', 'png', 'gif', 'webp'}:
                return Response({'detail': '图片内容校验失败'}, status=status.HTTP_400_BAD_REQUEST)

        media_type = 'image' if is_image else 'video'
        att = TicketAttachment.objects.create(
            ticket=ticket,
            media_type=media_type,
            file=upload,
            original_name=name
        )
        url = att.file.url if att.file else ''
        if url and not url.startswith('http'):
            url = request.build_absolute_uri(url)
        return Response({'id': att.id, 'media_type': att.media_type, 'url': url, 'original_name': att.original_name}, status=201)


class ServiceStarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceStar.objects.filter(is_active=True).order_by('sort_order', '-id')
    serializer_class = ServiceStarSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    user = request.user
    if user.role != 'student':
        return Response({"detail": "AI 助手仅面向学生开放"}, status=status.HTTP_403_FORBIDDEN)

    content = (request.data.get('message') or request.data.get('content') or '').strip()
    if not content:
        return Response({"detail": "问题内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)

    def _mask_pii(text: str) -> str:
        text = re.sub(r'\b1\d{10}\b', '[已脱敏手机号]', text)
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[已脱敏邮箱]', text)
        text = re.sub(r'\b\d{6,}\b', '[已脱敏数字]', text)
        text = re.sub(r'[A-Za-z0-9_\-]{24,}', '[已脱敏标识]', text)
        return text

    api_key = os.environ.get('AI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    base_url = (os.environ.get('AI_BASE_URL') or 'https://api.siliconflow.cn/v1').rstrip('/')
    model = os.environ.get('AI_MODEL') or 'deepseek-ai/DeepSeek-V3'
    try:
        timeout = float(os.environ.get('AI_TIMEOUT') or 20)
    except Exception:
        timeout = 20.0

    s = AiSetting.objects.order_by('-updated_at', '-id').first()
    if s:
        if not s.enabled:
            return Response({"detail": "AI 助手已在后台关闭"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if (s.api_base_url or '').strip():
            base_url = s.api_base_url.strip().rstrip('/')
        if (s.api_model or '').strip():
            model = s.api_model.strip()
        if (s.api_key or '').strip():
            api_key = s.api_key.strip()
        if getattr(s, 'timeout_seconds', None):
            try:
                timeout = float(s.timeout_seconds)
            except Exception:
                pass

    normalized = content.lower()
    category = "其他"
    if any(k in normalized for k in ["wifi", "wi-fi", "网络", "上网", "断网", "路由", "宽带"]):
        category = "网络连接"
    elif any(k in normalized for k in ["水", "漏水", "水龙头", "下水", "电", "灯", "跳闸", "插座", "电闸", "开关"]):
        category = "水电问题"
    elif any(k in normalized for k in ["空调", "冰箱", "洗衣机", "热水器", "风扇", "设备", "电器"]):
        category = "设备故障"
    elif any(k in normalized for k in ["柜", "衣柜", "桌", "椅", "床"]):
        category = "柜子损坏"
    elif any(k in normalized for k in ["门", "窗", "锁", "玻璃"]):
        category = "门窗损坏"

    name = user.name or user.username
    base = (
        f"您好，{name}。\n"
        f"我理解你遇到的问题是：{content}\n\n"
        f"建议（参考）：\n"
    )

    steps = []
    questions = []

    if category == "水电问题":
        steps = [
            "1）如有异味/冒烟/漏电/插座或电器发热/频繁跳闸：请立即停止使用，远离危险区域，不要触碰裸露线路或电器内部。",
            "2）不要自行拆插座、开电箱、测电或接线；这些属于高风险操作。",
            "3）请在平台【提交报修】选择“水电问题”，尽量描述现象（例如：哪盏灯、哪个插座、是否全宿舍断电），并上传现场照片。",
            "4）如果是漏水：尽量关闭可见阀门/水源（在确保安全前提下），并在平台备注“是否持续渗漏、是否影响邻室”。",
        ]
        questions = [
            "是否只影响你宿舍，还是同楼层/整层也有类似情况？",
            "是否出现跳闸、异味、火花、发热等明显危险信号？",
            "发生位置在哪里（楼栋-房间-具体点位）？",
        ]
    elif category == "网络连接":
        steps = [
            "1）先判断范围：是仅你设备不能上网，还是同宿舍同学也都不行。",
            "2）可尝试非破坏性操作：重新连接 Wi-Fi、关闭再打开飞行模式、重启设备网络。",
            "3）请在平台【提交报修】选择“网络连接”，补充错误提示/截图、发生时间段、影响范围。",
        ]
        questions = [
            "是连不上 Wi‑Fi，还是能连上但无法上网？",
            "手机/电脑是否都一样，还是某一台设备的问题？",
            "是否有错误提示截图（例如认证失败、无法获取IP等）？",
        ]
    elif category == "设备故障":
        steps = [
            "1）请不要自行拆机、拆插头或对电器内部进行任何检修。",
            "2）若设备显示错误代码/报警灯，请拍照记录；如果有异味/冒烟/异常发热，请立即停止使用。",
            "3）请在平台【提交报修】选择“设备故障”，填写设备名称、故障现象、出现时间与影响程度。",
        ]
        questions = [
            "设备是什么（空调/洗衣机/热水器等），型号或张贴编号有吗？",
            "故障是间歇还是持续，是否可复现？",
            "是否出现异味、冒烟、漏水、异常声音？",
        ]
    elif category == "门窗损坏":
        steps = [
            "1）请不要强行撬/砸/硬拧，以免造成二次损坏或夹伤。",
            "2）如涉及安全（门锁失效、玻璃破裂等），请保持现场安全并避免接触锋利边缘。",
            "3）请在平台【提交报修】选择“门窗损坏”，拍照并说明损坏位置与是否影响出入/通风/安全。",
        ]
        questions = [
            "是门锁问题还是门窗框/合页/玻璃问题？",
            "是否影响正常出入或存在割伤风险？",
        ]
    elif category == "柜子损坏":
        steps = [
            "1）不要强行拉拽/继续使用卡住的抽屉或柜门，以免夹伤或扩大损坏。",
            "2）请在平台【提交报修】选择“柜子损坏”，拍照并描述损坏部位（铰链/滑轨/门板等）。",
        ]
        questions = [
            "是柜门关不上、抽屉卡住，还是结构松动/断裂？",
            "是否影响正常使用或存在夹手风险？",
        ]
    else:
        steps = [
            f"1）你可以在平台【提交报修】选择最接近的类别（建议：{category}），填写地点、联系方式与现象描述。",
            "2）不要自行进行拆装、带电检修或任何高风险操作。",
            "3）建议附上照片/视频与发生时间，便于快速定位。",
        ]
        questions = [
            "问题具体发生在什么位置（楼栋-房间-点位）？",
            "是否影响安全或正常生活（例如漏水、跳闸、异味等）？",
        ]

    answer = base + "\n".join(steps)
    if questions:
        answer += "\n\n为了更准确一些，你可以补充：\n" + "\n".join([f"- {q}" for q in questions])
    answer += f"\n\n建议报修类别：{category}"

    warning = "重要提示：AI 提供的建议请仅供参考，以实际为准，不能盲目操作。"
    
    # 默认返回数据（fallback 模式）
    res_data = {
        "answer": answer,
        "warning": warning,
        "mode": "fallback",
        "ai_enabled": bool(api_key)
    }

    if api_key:
        if not base_url.startswith('https://'):
            # 如果配置不安全，直接走 fallback
            pass
        else:
            outbound_content = _mask_pii(content)
            system_prompt = (
                "你是校园报修AI助手。请用中文回答，回答要保守、谨慎、以安全为先。"
                "你只能提供报修流程、信息收集建议与风险提示，不能提供任何带电检修、拆装、测电等操作指导。"
                "遇到宿舍水电、安全风险、冒烟、漏电、跳闸等情况，必须提醒用户停止操作并通过平台提交报修等待处理。"
                "不要编造事实或承诺。回答末尾不要重复免责声明，免责声明由前端单独展示。"
            )
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": outbound_content},
                ],
                "temperature": 0.2,
            }
            logger = logging.getLogger(__name__)
            try:
                req = Request(
                    f"{base_url}/chat/completions",
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                msg = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
                if msg:
                    res_data = {"answer": msg, "warning": warning, "mode": "llm", "ai_enabled": True}
            except HTTPError as e:
                logger.warning("ai_chat_http_error", exc_info=True)
                res_data["upstream_status"] = getattr(e, "code", None)
            except URLError:
                logger.warning("ai_chat_url_error", exc_info=True)
            except Exception:
                logger.warning("ai_chat_error", exc_info=True)

    # 在返回之前，先在后台留个痕迹（保存日志）
    try:
        AiChatLog.objects.create(
            user=user,
            question=content,
            answer=res_data.get("answer", ""),
            mode=res_data.get("mode", ""),
            ai_enabled=res_data.get("ai_enabled", True),
            warning=res_data.get("warning", "")
        )
    except Exception as log_err:
        logging.getLogger(__name__).error(f"Failed to save AiChatLog: {log_err}")

    return Response(res_data)


# def change_status(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#
#     # 简单的状态流转逻辑
#     if order.status == 0:  # 待接单 -> 维修中
#         order.status = 1
#     elif order.status == 1:  # 维修中 -> 已完成
#         order.status = 2
#
#     order.save()
#
#     # 关键修改：返回 JSON 给 Vue，告诉它最新的状态是多少
#     return JsonResponse({
#         'code': 200,
#         'msg': '状态更新成功',
#         'new_status': order.status
#     })
