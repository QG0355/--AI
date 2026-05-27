from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_api', '0037_auditorprofile_contact_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='expected_finish_days',
            field=models.PositiveIntegerField(default=0, verbose_name='特殊处理预计天数'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='last_urge_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='上次催单时间'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='special_reason',
            field=models.TextField(blank=True, default='', verbose_name='特殊处理说明'),
        ),
    ]

