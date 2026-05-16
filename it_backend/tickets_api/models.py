from django.db import models
from django.contrib.auth.models import AbstractUser


def _user_avatar_upload_to(instance, filename):
    import os
    import uuid
    ext = os.path.splitext(filename)[1].lower()
    return f"avatars/{instance.pk}/{uuid.uuid4().hex}{ext}"


class CustomUser(AbstractUser):
    IDENTITY_CHOICES = (
        ('student', '学生'),
        ('maintenance', '维修人员'),
        ('auditor', '审核员'),
        ('admin', '超级管理员'),
    )

    GENDER_CHOICES = (
        ('unknown', '未知'),
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=100, blank=True, verbose_name="真实姓名")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unknown', verbose_name="性别")
    avatar_url = models.URLField(blank=True, default='', verbose_name="头像地址")
    avatar = models.FileField(upload_to=_user_avatar_upload_to, blank=True, null=True, verbose_name="头像文件")
    role = models.CharField(max_length=20, choices=IDENTITY_CHOICES, default='student', verbose_name="身份角色")
    identity_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="身份ID")
    is_identity_bound = models.BooleanField(default=False, verbose_name="是否已绑定")

    def __str__(self):
        return self.username


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('设备故障', '设备故障'),
        ('水电问题', '水电问题'),
        ('网络连接', '网络连接'),
        ('柜子损坏', '柜子损坏'),
        ('门窗损坏', '门窗损坏'),
        ('其他', '其他')
    ]

    PRIORITY_CHOICES = [('低', '低'), ('中', '中'), ('高', '高'), ('紧急', '紧急')]

    STATUS_CHOICES = [
        ('pending_dorm', '待审核员审核'),
        ('pending_dispatch', '待派单'),
        ('repairing', '维修中'),
        ('finished', '维修完成(待评价)'),
        ('closed', '已结单'),
        ('rejected', '已驳回')
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_dorm')
    description = models.TextField(blank=True, null=True, verbose_name="故障描述")

    location = models.CharField(max_length=200, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)

    submitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_tickets',
                                  verbose_name="提交人")
    assignee = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_tickets', verbose_name="维修人员")

    evaluation = models.TextField(blank=True, null=True, verbose_name="学生评价")
    rating = models.IntegerField(default=5, verbose_name="评分(1-5)")
    is_anonymous = models.BooleanField(default=False, verbose_name="是否匿名评价")
    rejected_reason = models.TextField(blank=True, null=True, verbose_name="驳回理由")

    submitTime = models.DateTimeField(auto_now_add=True)
    updateTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)


class Order(models.Model):

    STATUS_CHOICES = (
        (0, '待接单'),  # 刚提交也是这个状态
        (1, '维修中'),  # 维修人员点击“接单”后
        (2, '已完成'),  # 修好后
    )

    status = models.IntegerField(verbose_name="当前状态", choices=STATUS_CHOICES, default=0)


class StudentStar(models.Model):
    name = models.CharField(max_length=50, verbose_name="姓名")
    major = models.CharField(max_length=100, blank=True, verbose_name="专业班级")
    grade = models.CharField(max_length=50, blank=True, verbose_name="年级")
    honor = models.CharField(max_length=200, blank=True, verbose_name="荣誉称号")
    description = models.TextField(blank=True, verbose_name="事迹简介")
    score = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, verbose_name="评分")
    score_count = models.IntegerField(default=0, verbose_name="评价人数")
    avatar_url = models.URLField(blank=True, verbose_name="头像地址")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")
    is_active = models.BooleanField(default=True, verbose_name="是否展示")

    def __str__(self):
        return self.name


def _ticket_media_upload_to(instance, filename):
    import os
    import uuid
    ext = os.path.splitext(filename)[1].lower()
    return f"tickets/{instance.ticket_id}/{uuid.uuid4().hex}{ext}"


class TicketAttachment(models.Model):
    MEDIA_CHOICES = (
        ('image', '图片'),
        ('video', '视频'),
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    file = models.FileField(upload_to=_ticket_media_upload_to)
    original_name = models.CharField(max_length=255, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket_id}-{self.media_type}"


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True, verbose_name="学号")

    def __str__(self):
        return self.student_id


class MaintenanceProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='maintenance_profile')
    worker_id = models.CharField(max_length=50, unique=True, verbose_name="维修人员工号")

    def __str__(self):
        return self.worker_id


class AuditorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='auditor_profile')
    auditor_id = models.CharField(max_length=50, unique=True, verbose_name="审核员工号")

    def __str__(self):
        return self.auditor_id
