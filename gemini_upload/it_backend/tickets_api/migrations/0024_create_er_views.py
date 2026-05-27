from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('tickets_api', '0023_alter_ticket_assignee_alter_ticket_auditor_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW `v_student` AS
            SELECT
                u.id AS user_pk,
                u.username,
                u.name,
                u.gender,
                u.identity_id AS student_no,
                sp.student_id,
                sp.submitted_count
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_studentprofile sp ON sp.user_id = u.id
            WHERE u.role = 'student';

            CREATE OR REPLACE VIEW `v_maintenance` AS
            SELECT
                u.id AS user_pk,
                u.username,
                u.name,
                u.gender,
                u.identity_id AS worker_no,
                mp.worker_id,
                mp.finished_count,
                mp.rating
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_maintenanceprofile mp ON mp.user_id = u.id
            WHERE u.role = 'maintenance';

            CREATE OR REPLACE VIEW `v_auditor` AS
            SELECT
                u.id AS user_pk,
                u.username,
                u.name,
                u.gender,
                u.identity_id AS auditor_no,
                ap.auditor_id,
                ap.audited_count
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_auditorprofile ap ON ap.user_id = u.id
            WHERE u.role = 'auditor';

            CREATE OR REPLACE VIEW `v_admin` AS
            SELECT
                u.id AS user_pk,
                u.username,
                u.name,
                u.gender,
                u.identity_id AS admin_no,
                ad.admin_id,
                ad.permission_level
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_adminprofile ad ON ad.user_id = u.id
            WHERE u.role = 'admin';

            CREATE OR REPLACE VIEW `v_ticket` AS
            SELECT
                t.id AS ticket_id,
                t.title,
                t.category,
                t.priority,
                t.status,
                t.location,
                t.contact,
                t.submitTime,
                t.updateTime,
                submitter.identity_id AS submitter_no,
                assignee.identity_id AS assignee_no,
                auditor.identity_id AS auditor_no
            FROM tickets_api_ticket t
            LEFT JOIN tickets_api_customuser submitter ON submitter.id = t.submitter_id
            LEFT JOIN tickets_api_customuser assignee ON assignee.id = t.assignee_id
            LEFT JOIN tickets_api_customuser auditor ON auditor.id = t.auditor_id;
            """,
            reverse_sql="""
            DROP VIEW IF EXISTS `v_ticket`;
            DROP VIEW IF EXISTS `v_admin`;
            DROP VIEW IF EXISTS `v_auditor`;
            DROP VIEW IF EXISTS `v_maintenance`;
            DROP VIEW IF EXISTS `v_student`;
            """,
        )
    ]

