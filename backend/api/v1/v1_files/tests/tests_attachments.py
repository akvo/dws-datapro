import os
from mis.settings import STORAGE_PATH
from django.test import TestCase
from django.core.management import call_command
from utils import storage
from unittest.mock import patch


def generate_file(filename: str, extension: str = "jpg"):
    filename = f"{filename}.{extension}"
    f = open(filename, "a")
    f.write("This is a test file!")
    f.close()
    return filename


class AttachmentUploadTest(TestCase):
    def setUp(self):
        call_command("administration_seeder", "--test")
        user_payload = {"email": "admin@akvo.org", "password": "Test105*"}
        user_response = self.client.post(
            "/api/v1/login", user_payload, content_type="application/json"
        )
        self.token = user_response.json().get("token")

    def test_attachment_upload(self):
        filename = generate_file(filename="test", extension="pdf")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            f"/api/v1/upload/attachments/?{params}",
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json()), ["message", "file"])
        uploaded_filename = response.json().get("file")
        uploaded_filename = uploaded_filename.split("/")[-1]
        self.assertTrue(
            storage.check(f"/attachments/{uploaded_filename}"),
            "File exists",
        )
        os.remove(f"{STORAGE_PATH}/attachments/{uploaded_filename}")
        os.remove(filename)

    def test_attachment_upload_with_params_query_question_id(self):
        filename = generate_file(filename="test", extension="pdf")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            f"/api/v1/upload/attachments/?{params}&question_id=1",
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.json()),
            ["message", "file", "question_id"]
        )
        self.assertEqual(
            response.json().get("question_id"),
            "1",
            "question_id is present in the response",
        )
        uploaded_filename = response.json().get("file")
        uploaded_filename = uploaded_filename.split("/")[-1]
        self.assertTrue(
            storage.check(f"/attachments/{uploaded_filename}"),
            "File exists",
        )
        os.remove(f"{STORAGE_PATH}/attachments/{uploaded_filename}")
        os.remove(filename)

    def test_wrong_extension_upload(self):
        filename = generate_file(filename="test", extension="txt")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            (
                f"/api/v1/upload/attachments/?{params}"
            ),
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            "File extension “txt” is not allowed. Allowed extensions are: pdf, docx, doc.",  # noqa
        )
        os.remove(filename)

    def test_empty_file_upload(self):
        filename = generate_file(filename="test", extension="pdf")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            (
                f"/api/v1/upload/attachments/?{params}"
            ),
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json()), ["message", "file"])
        uploaded_filename = response.json().get("file")
        uploaded_filename = uploaded_filename.split("/")[-1]
        self.assertTrue(
            storage.check(f"/attachments/{uploaded_filename}"),
            "File exists",
        )
        os.remove(f"{STORAGE_PATH}/attachments/{uploaded_filename}")
        os.remove(filename)

    def test_file_upload_with_no_extension(self):
        filename = generate_file(filename="test", extension="")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            (
                f"/api/v1/upload/attachments/?{params}"
            ),
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            "File extension “” is not allowed. Allowed extensions are: pdf, docx, doc.",  # noqa
        )
        os.remove(filename)

    def test_file_upload_with_no_file(self):
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        response = self.client.post(
            (
                f"/api/v1/upload/attachments/?{params}"
            ),
            {},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            "No file was submitted in file.",
        )

    def test_file_upload_with_no_allowed_file_types(self):
        filename = generate_file(filename="test", extension="pdf")
        params = "&".join(
            f"allowed_file_types={ext}" for ext in []
        )
        response = self.client.post(
            (
                f"/api/v1/upload/attachments/?{params}"
            ),
            {"file": open(filename, "rb")},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.json()), ["message", "file"])
        uploaded_filename = response.json().get("file")
        uploaded_filename = uploaded_filename.split("/")[-1]
        self.assertTrue(
            storage.check(f"/attachments/{uploaded_filename}"),
            "File exists",
        )
        os.remove(f"{STORAGE_PATH}/attachments/{uploaded_filename}")
        os.remove(filename)

    def test_failed_upload_return_500(self):
        filename = generate_file(filename="test", extension="pdf")
        allowed_file_types = [
            "pdf",
            "docx",
            "doc",
        ]
        params = "&".join(
            f"allowed_file_types={ext}" for ext in allowed_file_types
        )
        with patch(
            "utils.storage.upload",
            side_effect=ZeroDivisionError("division by zero")
        ):
            response = self.client.post(
                f"/api/v1/upload/attachments/?{params}",
                {"file": open(filename, "rb")},
                HTTP_AUTHORIZATION=f"Bearer {self.token}",
            )
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.json(),
                {
                    "message": "File upload failed",
                    "error": "division by zero",
                },
            )
        os.remove(filename)
