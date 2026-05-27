from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets_api', '0036_maintenanceprofile_is_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditorprofile',
            name='contact_phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='联系电话'),
        ),
    ]

