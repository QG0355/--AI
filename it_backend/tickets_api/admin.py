from django.contrib import admin
from .models import Ticket, StudentStar, CustomUser, TicketAttachment


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'submitter', 'assignee', 'submitTime')
    list_filter = ('category', 'status')
    search_fields = ('title', 'description', 'location', 'submitter__username')


@admin.register(StudentStar)
class StudentStarAdmin(admin.ModelAdmin):
    list_display = ('name', 'major', 'grade', 'honor', 'score', 'score_count', 'sort_order', 'is_active')
    list_editable = ('score', 'score_count', 'sort_order', 'is_active')
    list_filter = ('grade', 'is_active')
    search_fields = ('name', 'major', 'honor')
    ordering = ('sort_order', '-id')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'role', 'identity_id', 'is_identity_bound', 'is_staff')
    list_filter = ('role', 'is_identity_bound', 'is_staff')
    search_fields = ('username', 'name', 'identity_id')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'media_type', 'original_name', 'uploaded_at')
    list_filter = ('media_type',)
    search_fields = ('ticket__title', 'original_name')
