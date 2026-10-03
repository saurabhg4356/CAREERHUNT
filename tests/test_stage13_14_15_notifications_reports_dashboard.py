"""
Stage 13, 14, and 15 verification tests for CareerHunt.
Validates Notifications, Job Alerts, Listing Reporting, and Admin Moderation Dashboard.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.sources.models import JobSource
from apps.jobs.models import Job
from apps.notifications.models import Notification, JobAlert
from apps.reports.models import Report


class Stage131415NotificationsReportsDashboardTestCase(TestCase):
    """
    Test suite for alerts, notifications, reports, and administrative telemetry.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="candidate_tom",
            password="StrongPassword123!",
            first_name="Tom",
        )
        self.staff_user = User.objects.create_user(
            username="staff_admin",
            password="AdminPassword123!",
            is_staff=True,
        )

        self.company = Company.objects.create(name="Oracle Labs")
        self.source = JobSource.objects.create(
            name="Oracle Official Careers",
            source_type="official_company",
            source_url="https://oracle.com/careers",
        )

        self.job = Job.objects.create(
            title="Database Systems Intern",
            company=self.company,
            source=self.source,
            opportunity_type="internship",
            experience_level="fresher",
            location_name="Bangalore",
            source_url="https://oracle.com/jobs/1",
            application_url="https://oracle.com/apply/1",
            description="Database kernels and SQL engines.",
        )

    def test_notifications_and_mark_read(self):
        """Verify notification creation and mark-as-read workflow."""
        notif = Notification.objects.create(
            user=self.user,
            title="Deadline Approaching",
            message="Your saved opportunity closes soon.",
            notification_type="deadline_approaching",
            target_url="/jobs/saved/",
        )

        self.client.login(username="candidate_tom", password="StrongPassword123!")

        # View notifications
        resp = self.client.get(reverse("notifications:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Deadline Approaching")

        # Mark single as read
        read_resp = self.client.get(reverse("notifications:mark_read", kwargs={"pk": notif.pk}))
        self.assertEqual(read_resp.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_job_alerts_crud(self):
        """Verify candidate job alerts creation and deletion."""
        self.client.login(username="candidate_tom", password="StrongPassword123!")

        # Create alert
        create_resp = self.client.post(reverse("notifications:alerts"), {
            "name": "Database Internships",
            "keywords": "SQL, C++, Database",
            "location": "Bangalore",
            "opportunity_type": "internship",
            "frequency": "daily",
        })
        self.assertEqual(create_resp.status_code, 302)

        alert = JobAlert.objects.get(user=self.user, name="Database Internships")
        self.assertEqual(alert.keywords, "SQL, C++, Database")

        # Delete alert
        del_resp = self.client.post(reverse("notifications:delete_alert", kwargs={"pk": alert.pk}))
        self.assertEqual(del_resp.status_code, 302)
        self.assertFalse(JobAlert.objects.filter(pk=alert.pk).exists())

    def test_listing_report_and_moderation(self):
        """Verify reporting an opportunity and admin moderation resolution."""
        # 1. Candidate reports opportunity
        self.client.login(username="candidate_tom", password="StrongPassword123!")
        report_resp = self.client.post(reverse("reports:submit_report", kwargs={"job_id": self.job.pk}), {
            "reason": "suspicious_link",
            "details": "Destination link redirects to an invalid marketing domain.",
        })
        self.assertEqual(report_resp.status_code, 302)

        report = Report.objects.get(job=self.job)
        self.assertEqual(report.status, "pending")
        self.assertEqual(report.reported_by, self.user)

        self.job.refresh_from_db()
        self.assertEqual(self.job.verification_status, "reported")

        # 2. Staff user reviews report and deactivates listing
        self.client.login(username="staff_admin", password="AdminPassword123!")
        resolve_resp = self.client.post(reverse("reports:resolve_report", kwargs={"pk": report.pk}), {
            "action": "resolve_disable",
            "admin_notes": "Confirmed broken redirect. Listing disabled.",
        })
        self.assertEqual(resolve_resp.status_code, 302)

        report.refresh_from_db()
        self.assertEqual(report.status, "resolved")
        self.assertEqual(report.reviewed_by, self.staff_user)

        self.job.refresh_from_db()
        self.assertEqual(self.job.status, "closed")

    def test_admin_dashboard_permissions_and_metrics(self):
        """Verify admin telemetry dashboard access controls and metrics."""
        # Non-staff denied
        self.client.login(username="candidate_tom", password="StrongPassword123!")
        denied_resp = self.client.get(reverse("dashboard:admin_dashboard"))
        self.assertEqual(denied_resp.status_code, 302)

        # Staff granted
        self.client.login(username="staff_admin", password="AdminPassword123!")
        dash_resp = self.client.get(reverse("dashboard:admin_dashboard"))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Platform Telemetry")
        self.assertContains(dash_resp, "Active Jobs")
        self.assertContains(dash_resp, "Oracle Official Careers")
