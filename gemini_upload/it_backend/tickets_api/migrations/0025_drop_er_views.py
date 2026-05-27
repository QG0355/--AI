from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('tickets_api', '0024_create_er_views'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW IF EXISTS `v_ticket`;
            DROP VIEW IF EXISTS `v_admin`;
            DROP VIEW IF EXISTS `v_auditor`;
            DROP VIEW IF EXISTS `v_maintenance`;
            DROP VIEW IF EXISTS `v_student`;
            """,
            reverse_sql="""
            """,
        )
    ]

