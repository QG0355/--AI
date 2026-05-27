from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('tickets_api', '0029_servicestar_worker'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW `student_user` AS
            SELECT
                u.id AS student_id,
                u.username,
                u.password,
                COALESCE(NULLIF(u.name, ''), u.username) AS name,
                u.gender,
                COALESCE(sp.submitted_count, 0) AS submitted_count
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_studentprofile sp ON sp.user_id = u.id
            WHERE u.role = 'student';

            CREATE OR REPLACE VIEW `worker_user` AS
            SELECT
                u.id AS worker_id,
                u.username,
                u.password,
                COALESCE(NULLIF(u.name, ''), u.username) AS name,
                u.gender,
                COALESCE(mp.finished_count, 0) AS finished_count,
                COALESCE(mp.rating, 5.00) AS rating
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_maintenanceprofile mp ON mp.user_id = u.id
            WHERE u.role = 'maintenance';

            CREATE OR REPLACE VIEW `auditor_user` AS
            SELECT
                u.id AS auditor_id,
                u.username,
                u.password,
                COALESCE(NULLIF(u.name, ''), u.username) AS name,
                ap.auditor_id AS auditor_job_no,
                COALESCE(ap.audited_count, 0) AS audited_count
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_auditorprofile ap ON ap.user_id = u.id
            WHERE u.role = 'auditor';

            CREATE OR REPLACE VIEW `admin_user` AS
            SELECT
                u.id AS admin_id,
                u.username,
                u.password,
                COALESCE(NULLIF(u.name, ''), u.username) AS name,
                COALESCE(ad.permission_level, 1) AS permission_level
            FROM tickets_api_customuser u
            LEFT JOIN tickets_api_adminprofile ad ON ad.user_id = u.id
            WHERE u.role = 'admin';

            CREATE OR REPLACE VIEW `service_star_info` AS
            SELECT
                s.id,
                s.name,
                s.honor,
                s.description,
                s.score,
                s.score_count,
                s.worker_id
            FROM tickets_api_servicestar s;

            CREATE OR REPLACE VIEW `ticket_info` AS
            SELECT
                t.id,
                t.title,
                t.category,
                t.priority,
                t.status,
                t.description,
                t.location,
                t.contact,
                t.submitter_id,
                t.assignee_id,
                t.auditor_id,
                t.evaluation,
                t.rating,
                t.rejected_reason,
                t.submitTime
            FROM tickets_api_ticket t;
            """,
            reverse_sql="""
            DROP VIEW IF EXISTS `ticket_info`;
            DROP VIEW IF EXISTS `service_star_info`;
            DROP VIEW IF EXISTS `admin_user`;
            DROP VIEW IF EXISTS `auditor_user`;
            DROP VIEW IF EXISTS `worker_user`;
            DROP VIEW IF EXISTS `student_user`;
            """,
        ),
    ]

