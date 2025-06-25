from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command

from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_data.models import FormData
from api.v1.v1_data.tasks import seed_approved_data
from api.v1.v1_users.models import SystemUser
from api.v1.v1_profile.constants import DataAccessTypes
from api.v1.v1_profile.tests.mixins import ProfileTestHelperMixin


@override_settings(USE_TZ=False, TEST_ENV=True)
class DataBatchApprovedTestCase(TestCase, ProfileTestHelperMixin):
    def setUp(self):
        call_command("administration_seeder", "--test", 1)
        call_command("default_roles_seeder", "--test", 1)
        call_command("form_seeder", "--test", 1)

        call_command("fake_data_seeder", "-r", 10, "-t", True)

        self.data = FormData.objects.filter(
            is_pending=True,
            administration__level__level=3,
        ).first()

        parent_adms = self.data.administration.ancestors.all()

        approver_list = []
        for p in parent_adms:
            da = DataAccessTypes.approve
            approver = SystemUser.objects.filter(
                user_user_role__administration=p,
                user_user_role__role__role_role_access__data_access=da,
            ).order_by("?").first()
            if not approver:
                # create a new approver
                new_approver = self.create_user(
                    email="new.approver@test.com",
                    role_level=self.IS_APPROVER,
                    administration=p,
                    form=self.data.form,
                )
                approver_list.append({
                    "level": p.level.level,
                    "user": new_approver,
                })
            else:
                approver_list.append({
                    "level": p.level.level,
                    "user": approver,
                })

        # Create a batch with the new data
        submitter = self.data.created_by
        submitter.set_password("test")
        submitter.save()

        submitter_token = self.get_auth_token(submitter.email, "test")
        payload = {
            "name": "Test Batch 2",
            "comment": "This is another test batch",
            "data": [self.data.id],
        }
        response = self.client.post(
            "/api/v1/batch",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {submitter_token}",
        )
        self.assertEqual(response.status_code, 201)
        self.data.refresh_from_db()

        self.batch = self.data.data_batch_list.batch

        # Get batch list by first level approver
        a1 = list(
            filter(
                lambda x: x["level"] == 0,
                approver_list
            )
        )[0]
        a1 = a1["user"]
        a1.set_password("test")
        a1.save()
        self.a1 = a1

        self.a1_token = self.get_auth_token(
            a1.email,
            "test"
        )

        # Get batch list by second level approver
        a2 = list(
            filter(
                lambda x: x["level"] == 1,
                approver_list
            )
        )[0]
        a2 = a2["user"]
        a2.set_password("test")
        a2.save()

        self.a2 = a2
        self.a2_token = self.get_auth_token(
            a2.email,
            "test"
        )

        # Get batch list by third level approver
        a3 = list(
            filter(
                lambda x: x["level"] == 2,
                approver_list
            )
        )[0]
        a3 = a3["user"]
        a3.set_password("test")
        a3.save()

        self.a3 = a3
        self.a3_token = self.get_auth_token(
            a3.email,
            "test"
        )

    def test_batch_approved_by_third_level_approver(self):
        response = self.client.get(
            "/api/v1/form-pending-batch",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a3_token}",
        )
        self.assertEqual(response.status_code, 200)
        batch = response.json()["batch"][0]
        approval = list(
            filter(
                lambda x: x["name"] == self.a3.get_full_name(),
                batch["approver"]
            )
        )[0]
        payload = {
            "approval": approval["id"],
            "status": DataApprovalStatus.approved,
            "comment": "Approved by third level approver",
        }
        # Approve the batch by third level approver
        response = self.client.post(
            "/api/v1/pending-data/approve",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a3_token}",
        )
        self.assertEqual(response.status_code, 200)

        # Check if the data is approved
        self.data.refresh_from_db()
        self.assertTrue(
            self.data.is_pending
        )

    def test_batch_approved_by_second_level_approver(self):
        # Approve the third level approver first
        third_approval = self.batch.batch_approval.filter(
            user=self.a3,
        ).first()
        third_approval.status = DataApprovalStatus.approved
        third_approval.save()

        response = self.client.get(
            "/api/v1/form-pending-batch",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a2_token}",
        )
        self.assertEqual(response.status_code, 200)
        batch = response.json()["batch"][0]
        approval = list(
            filter(
                lambda x: x["name"] == self.a2.get_full_name(),
                batch["approver"]
            )
        )[0]

        payload = {
            "approval": approval["id"],
            "status": DataApprovalStatus.approved,
            "comment": "Approved by second level approver",
        }
        # Approve the batch by second level approver
        response = self.client.post(
            "/api/v1/pending-data/approve",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a2_token}",
        )
        self.assertEqual(response.status_code, 200)
        # Check if the data is approved
        self.data.refresh_from_db()
        self.assertTrue(
            self.data.is_pending
        )

    def test_batch_approved_by_first_level_approver(self):
        # Approve the third and second level approvers first
        third_approval = self.batch.batch_approval.filter(
            user=self.a3,
        ).first()
        third_approval.status = DataApprovalStatus.approved
        third_approval.save()

        second_approval = self.batch.batch_approval.filter(
            user=self.a2,
        ).first()
        second_approval.status = DataApprovalStatus.approved
        second_approval.save()

        # Now approve by first level approver
        response = self.client.get(
            "/api/v1/form-pending-batch",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a1_token}",
        )
        self.assertEqual(response.status_code, 200)
        batch = response.json()["batch"][0]

        approval = list(
            filter(
                lambda x: x["name"] == self.a1.get_full_name(),
                batch["approver"]
            )
        )[0]
        payload = {
            "approval": approval["id"],
            "status": DataApprovalStatus.approved,
            "comment": "Approved by first level approver",
        }
        # Approve the batch by first level approver
        response = self.client.post(
            "/api/v1/pending-data/approve",
            payload,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.a1_token}",
        )
        self.assertEqual(response.status_code, 200)
        # Check if the data is approved
        self.batch.refresh_from_db()
        self.assertTrue(
            self.batch.approved
        )

        seed_approved_data(self.data)

        self.data.refresh_from_db()
        self.assertFalse(
            self.data.is_pending
        )
