from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from .models import Ticket, ServiceStar, CustomUser, TicketAttachment, AiChatLog, StudentProfile, MaintenanceProfile, AuditorProfile, AdminProfile

# 隐藏不需要的默认模块（认证与授权、Token等）
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'submitted_count')


@admin.register(MaintenanceProfile)
class MaintenanceProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'worker_id', 'finished_count', 'rating')


@admin.register(AuditorProfile)
class AuditorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'auditor_id', 'audited_count')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin_id', 'permission_level')


@admin.register(AiChatLog)
class AiChatLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'mode', 'ai_enabled', 'created_at')
    list_filter = ('mode', 'ai_enabled', 'created_at')
    search_fields = ('user__username', 'question', 'answer')
    readonly_fields = ('user', 'question', 'answer', 'mode', 'ai_enabled', 'warning', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'submitter', 'assignee', 'auditor', 'submitTime')
    list_filter = ('category', 'status')
    search_fields = ('title', 'description', 'location', 'submitter__username', 'auditor__username')


@admin.register(ServiceStar)
class ServiceStarAdmin(admin.ModelAdmin):
    list_display = ('name', 'honor', 'score', 'score_count', 'sort_order', 'is_active')
    list_editable = ('score', 'score_count', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'honor')
    ordering = ('sort_order', '-id')


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = '学生详情'

class MaintenanceProfileInline(admin.StackedInline):
    model = MaintenanceProfile
    can_delete = False
    verbose_name_plural = '维修员详情'

class AuditorProfileInline(admin.StackedInline):
    model = AuditorProfile
    can_delete = False
    verbose_name_plural = '审核员详情'

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = '管理员详情'

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # 列表页展示的字段
    list_display = ('username', 'name', 'role', 'identity_id', 'is_identity_bound')
    # 右侧筛选器
    list_filter = ('role', 'is_identity_bound')
    # 搜索框
    search_fields = ('username', 'name', 'identity_id')
    
    # 自动关联对应的详情表
    inlines = [StudentProfileInline, MaintenanceProfileInline, AuditorProfileInline, AdminProfileInline]
    
    # 修改/添加用户时展示的字段（精简版）
    fieldsets = (
        ('基础信息', {
            'fields': ('username', 'password', 'name', 'gender', 'role')
        }),
        ('身份绑定', {
            'fields': ('identity_id', 'is_identity_bound')
        }),
        ('头像', {
            'fields': ('avatar', 'avatar_url')
        }),
    )

    def save_model(self, request, obj, form, change):
        # 如果是新创建用户且设置了密码，需要加密保存
        if not change:
            obj.set_password(obj.password)
        
        # 如果角色是管理员或审核员，自动赋予登录后台的权限
        if obj.role in ['admin', 'auditor']:
            obj.is_staff = True
        else:
            obj.is_staff = False
            
        super().save_model(request, obj, form, change)


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'media_type', 'original_name', 'uploaded_at')
    list_filter = ('media_type',)
    search_fields = ('ticket__title', 'original_name')
