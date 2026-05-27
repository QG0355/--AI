from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_api', '0027_remove_auditorprofile_assigned_worker'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='response_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='响应时间'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='repair_result',
            field=models.TextField(blank=True, null=True, verbose_name='维修结果'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='materials_used',
            field=models.TextField(blank=True, null=True, verbose_name='耗材使用'),
        ),
    ]

