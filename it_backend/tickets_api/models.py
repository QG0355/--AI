from django.db import models
from django.contrib.auth.models import AbstractUser


# 1. 自定义用户模型 (包含身份和权限)
class CustomUser(AbstractUser):
    IDENTITY_CHOICES = (
        ('student', '学生'),
        ('teacher', '老师'),
        ('dorm_manager', '宿管'),
        ('building_manager', '教学楼管理员'),
        ('admin', '系统管理员'),
    )

    # 基本信息
    name = models.CharField(max_length=100, blank=True, verbose_name="真实姓名")
    role = models.CharField(max_length=20, choices=IDENTITY_CHOICES, default='student', verbose_name="身份角色")

    # 身份绑定核心字段
    identity_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="学号/工号")
    is_identity_bound = models.BooleanField(default=False, verbose_name="是否已绑定身份")

    # 临时权限列表 (JSON格式存储，例如 ['teaching_building', 'office'])
    extra_permissions = models.JSONField(default=list, blank=True, verbose_name="额外区域权限")

    def __str__(self):
        return self.username


# 2. OA 审批单模型
class OARequest(models.Model):
    STATUS_CHOICES = (
        ('pending_teacher', '待老师审批'),
        ('pending_admin', '待管理员审批'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )

    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='oa_requests')
    target_area = models.CharField(max_length=50, verbose_name="申请报修区域")
    reason = models.TextField(verbose_name="申请理由")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_teacher')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.requester.name} 申请 {self.target_area}"


# 3. 报修单模型
class Ticket(models.Model):
    CATEGORY_CHOICES = [('硬件故障', '硬件故障'), ('软件问题', '软件问题'), ('网络连接', '网络连接'),
                        ('系统权限', '系统权限'), ('打印机问题', '打印机问题'), ('其他', '其他')]
    PRIORITY_CHOICES = [('低', '低'), ('中', '中'), ('高', '高'), ('紧急', '紧急')]
    STATUS_CHOICES = [('待处理', '待处理'), ('处理中', '处理中'), ('已完成', '已完成'), ('已关闭', '已关闭')]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='待处理')
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)

    # 关联用户
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_tickets')
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tickets')

    submitTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# 4. 评论模型
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)