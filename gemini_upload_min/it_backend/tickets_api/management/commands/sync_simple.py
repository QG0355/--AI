from django.core.management.base import BaseCommand
from tickets_api.models import CustomUser, Ticket, ServiceStar
from tickets_api.simple_sync import sync_user, sync_ticket, sync_service_star


class Command(BaseCommand):
    help = "把当前 Django 数据同步写入 BiShe_simple（论文用简化库）"

    def handle(self, *args, **options):
        for u in CustomUser.objects.all().iterator():
            sync_user(u)
        for s in ServiceStar.objects.all().iterator():
            sync_service_star(s)
        for t in Ticket.objects.all().iterator():
            sync_ticket(t)
        self.stdout.write(self.style.SUCCESS("sync_simple 完成"))

