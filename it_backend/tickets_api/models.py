from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    IDENTITY_CHOICES = (
        ('student', '学生'),
        ('teacher', '老师'),
        ('dorm_manager', '宿管'),
        ('building_manager', '教学楼管理员'),
        ('maintenance', '维修人员'),
        ('repair_admin', '报修管理员(审核/派单)'),  # <--- 新增角色
        ('admin', '系统管理员'),
    )

    name = models.CharField(max_length=100, blank=True, verbose_name="真实姓名")
    role = models.CharField(max_length=20, choices=IDENTITY_CHOICES, default='student', verbose_name="身份角色")
    identity_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="学号/工号")
    is_identity_bound = models.BooleanField(default=False, verbose_name="是否已绑定身份")
    extra_permissions = models.JSONField(default=list, blank=True, verbose_name="额外区域权限")

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class OARequest(models.Model):
    # (OA 模型保持不变，为了节省篇幅这里省略，请保留你原有的 OARequest 代码)
    # ... 请把之前的 OARequest 代码粘贴在这里 ...
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


class Ticket(models.Model):
    CATEGORY_CHOICES = [('硬件故障', '硬件故障'), ('软件问题', '软件问题'), ('网络连接', '网络连接'),
                        ('系统权限', '系统权限'), ('打印机问题', '打印机问题'), ('其他', '其他')]
    PRIORITY_CHOICES = [('低', '低'), ('中', '中'), ('高', '高'), ('紧急', '紧急')]

    # --- ⭐ 核心升级：状态流转链 ⭐ ---
    STATUS_CHOICES = [
        ('pending_dorm', '待宿管审核'),  # 学生提交 -> 宿管看
        ('pending_dispatch', '待派单审核'),  # 宿管通过/老师提交 -> 报修管理员看
        ('repairing', '维修中'),  # 管理员派单 -> 维修人员看
        ('finished', '维修完成(待评价)'),  # 维修人员点完成 -> 学生看
        ('closed', '已结单'),  # 学生评价完 -> 结束
        ('rejected', '已驳回')  # 审核不通过
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_dispatch')
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)

    # 关联用户
    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_tickets',
                                  verbose_name="提交人")
    # 维修人员 (由报修管理员指派)
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tickets', verbose_name="维修人员")

    # 评价字段
    evaluation = models.TextField(blank=True, null=True, verbose_name="学生评价")
    rating = models.IntegerField(default=5, verbose_name="评分(1-5)")

    submitTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    # (Comment 模型保持不变)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)