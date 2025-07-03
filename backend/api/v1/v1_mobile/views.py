import os
from typing import cast
import requests
import mimetypes
from rest_framework.request import Request

from rest_framework.viewsets import ModelViewSet
from api.v1.v1_mobile.authentication import (
    IsMobileAssignment,
    MobileAssignmentToken,
)
from mis.settings import (
    MASTER_DATA,
    BASE_DIR,
    APK_UPLOAD_SECRET,
    APK_SHORT_NAME,
    WEBDOMAIN,
)
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q

from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    inline_serializer,
)

from utils.custom_pagination import Pagination
from .serializers import (
    MobileAssignmentFormsSerializer,
    MobileApkSerializer,
    MobileAssignmentSerializer,
    MobileDataPointDownloadListSerializer,
    SyncDeviceFormDataSerializer,
)
from .models import MobileAssignment, MobileApk
from api.v1.v1_forms.models import Forms, Questions, QuestionTypes
from api.v1.v1_data.models import FormData
from api.v1.v1_forms.serializers import WebFormDetailSerializer
from api.v1.v1_data.serializers import (
    SubmitPendingFormSerializer,
    SubmitUpdateDraftFormSerializer,
)
from api.v1.v1_files.serializers import (
    UploadImagesSerializer,
    AttachmentsSerializer,
)
from api.v1.v1_profile.constants import DataAccessTypes
from api.v1.v1_profile.models import Administration
from api.v1.v1_files.functions import handle_upload
from utils.custom_helper import CustomPasscode
from utils.default_serializers import DefaultResponseSerializer
from utils.custom_serializer_fields import (
    validate_serializers_message,
)
from utils import storage

apk_path = os.path.join(BASE_DIR, MASTER_DATA)


@extend_schema(
    request=MobileAssignmentFormsSerializer,
    responses={200: MobileAssignmentFormsSerializer},
    tags=["Mobile Device Form"],
    summary="To get list of mobile forms",
    description="To get list of mobile forms",
)
@api_view(["POST"])
def get_mobile_forms(request, version):
    code = request.data.get("code")
    serializer = MobileAssignmentFormsSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        passcode = CustomPasscode().encode(code)
        mobile_assignment = MobileAssignment.objects.get(passcode=passcode)
        mobile_assignment.last_synced_at = None
        mobile_assignment.save()
    except MobileAssignment.DoesNotExist:
        return Response(
            {"error": "Mobile Assignment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = MobileAssignmentFormsSerializer(mobile_assignment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: WebFormDetailSerializer},
    tags=["Mobile Device Form"],
    summary="To get form in mobile form format",
)
@api_view(["GET"])
@permission_classes([IsMobileAssignment])
def get_mobile_form_details(request: Request, version, form_id):
    instance = get_object_or_404(Forms, pk=form_id)
    assignment = cast(MobileAssignmentToken, request.auth).assignment
    data = WebFormDetailSerializer(
        instance=instance,
        context={
            "user": assignment.user,
            "mobile_assignment": assignment,
        },
    ).data
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    request=SyncDeviceFormDataSerializer,
    responses={200: DefaultResponseSerializer},
    tags=["Mobile Device Form"],
    parameters=[
        OpenApiParameter(
            name="is_draft",
            required=False,
            default=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="is_published",
            required=False,
            default=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
        ),
    ],
    summary="Submit pending form data",
)
@api_view(["POST"])
@permission_classes([IsMobileAssignment])
def sync_pending_form_data(request, version):
    form = get_object_or_404(Forms, pk=request.data.get("formId"))
    assignment = cast(MobileAssignmentToken, request.auth).assignment
    user = assignment.user
    administration = assignment.administrations.order_by(
        "level__level"
    ).first()
    if user.user_user_role.exists():
        user_role = user.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first()
        if user_role:
            # If user has a role with data access, use that administration
            administration = user_role.administration

    if not request.data.get("answers"):
        return Response(
            {"message": "Answers is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    answers = []
    qna = request.data.get("answers")
    adm_id = administration.id
    adm_qs = Questions.objects.filter(
        type=QuestionTypes.administration, form_id=form.id
    ).first()
    adm_key = str(adm_qs.id) if adm_qs else None
    if adm_key and adm_key in qna:
        adm_id = qna[adm_key]
    # Handle repeat question values with indexes
    for q_key in list(qna):
        """
        Extract the base question ID from the key
        Keys can be like "1" or "1-1" or "1-2"
        where the base question ID is "1"
        """
        index = 0
        if '-' in str(q_key):
            [base_q_id, q_index] = str(q_key).split('-')
            index = q_index
        else:
            base_q_id = str(q_key)
        answers.append({
            "question": base_q_id,
            "value": qna[q_key],
            "index": index,
        })
    payload = {
        "administration": adm_id,
        "name": request.data.get("name"),
        "geo": request.data.get("geo"),
        "submitter": assignment.name,
        "duration": request.data.get("duration"),
    }
    if request.data.get("uuid"):
        payload["uuid"] = request.data["uuid"]
    data = {
        "data": payload,
        "answer": answers,
    }
    is_draft = request.GET.get("is_draft", False)
    is_draft = True if is_draft in ["true", "True", "1"] else False
    serializer = SubmitPendingFormSerializer(
        data=data,
        context={
            "user": user,
            "form": form,
            "is_draft": is_draft,
        }
    )
    draft_exists = FormData.objects_draft.filter(
        form=form,
        created_by=user,
        uuid=request.data.get("uuid"),
    ).first()
    if draft_exists:
        serializer = SubmitUpdateDraftFormSerializer(
            instance=draft_exists,
            data=data,
            context={
                "user": user
            }
        )
    if not serializer.is_valid():
        return Response(
            {
                "message": validate_serializers_message(serializer.errors),
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    is_published = request.GET.get("is_published", False)
    is_published = True if is_published in ["true", "True", "1"] else False
    if is_published and draft_exists:
        draft_exists.publish()
    return Response({"message": "ok"}, status=status.HTTP_200_OK)


@extend_schema(tags=["Mobile Device Form"], summary="Get SQLITE File")
@api_view(["GET"])
def download_sqlite_file(request, version, file_name):
    file_path = os.path.join(BASE_DIR, MASTER_DATA, f"{file_name}")

    # Make sure the file exists and is accessible
    if not os.path.exists(file_path):
        return HttpResponse(
            {"message": "File not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Get the file's content type
    content_type, _ = mimetypes.guess_type(file_path)

    # Read the file content into a variable
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Create the response and set the appropriate headers
    response = HttpResponse(file_content, content_type=content_type)
    response["Content-Length"] = os.path.getsize(file_path)
    response["Content-Disposition"] = "attachment; filename=%s" % file_name
    return response


@extend_schema(
    tags=["Mobile Device Form"],
    summary="Upload Images from Device",
    request=UploadImagesSerializer,
    responses={
        (200, "application/json"): inline_serializer(
            "UploadImagesFromDevice",
            fields={
                "message": serializers.CharField(),
                "file": serializers.CharField(),
            },
        )
    },
)
@api_view(["POST"])
@permission_classes([IsMobileAssignment])
@parser_classes([MultiPartParser])
def upload_image_form_device(request, version):
    serializer = UploadImagesSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            validate_serializers_message(serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )
    filename = handle_upload(request=request, folder="images")
    return Response(
        {
            "message": "File uploaded successfully",
            "file": f"{WEBDOMAIN}/images/{filename}",
        },
        status=status.HTTP_200_OK,
    )


class UploadAttachmentsView(APIView):
    permission_classes = [IsMobileAssignment]
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["Mobile Device Form"],
        summary="Upload Attachments from Device",
        request=AttachmentsSerializer,
        parameters=[
            OpenApiParameter(
                name="allowed_file_types",
                required=False,
                location=OpenApiParameter.QUERY,
                description=(
                    "List of allowed file types for the attachment. "
                ),
                type={"type": "array", "items": {"type": "string"}},
                enum=[
                    "pdf", "docx", "xlsx", "pptx", "txt", "csv", "zip", "rar",
                    "jpg", "jpeg", "png", "gif", "bmp", "doc", "xls", "ppt",
                    "mp4", "avi", "mov", "mkv", "flv", "wmv", "mp3", "wav",
                    "ogg", "flac", "aac", "wma", "m4a", "opus", "webm", "3gp",
                ],
            )
        ],
        responses={
            (200, "application/json"): inline_serializer(
                "UploadAttachmentsFromDevice",
                fields={
                    "message": serializers.CharField(),
                    "file": serializers.CharField(),
                },
            )
        },
    )
    def post(self, request, version):
        allowed_file_types = request.GET.getlist("allowed_file_types")
        serializer = AttachmentsSerializer(
            data=request.data,
            context={
                "allowed_file_types": allowed_file_types,
            },
        )
        if not serializer.is_valid():
            return Response(
                validate_serializers_message(serializer.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:

            filename = handle_upload(request=request, folder="attachments")
            return Response(
                {
                    "message": "File uploaded successfully",
                    "file": f"{WEBDOMAIN}/attachments/{filename}",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "message": "File upload failed.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Mobile APK"], summary="Get APK File")
@api_view(["GET"])
def download_apk_file(request, version):
    apk = MobileApk.objects.last()
    if not apk:
        return Response(
            {"message": "APK not found."}, status=status.HTTP_404_NOT_FOUND
        )
    file_name = f"{APK_SHORT_NAME}-{apk.apk_version}.apk"
    cache_file_name = os.path.join(apk_path, file_name)
    if os.path.exists(cache_file_name):
        # Get the file's content type
        content_type, _ = mimetypes.guess_type(cache_file_name)
        # Read the file content into a variable
        with open(cache_file_name, "rb") as file:
            file_content = file.read()
        # Create the response and set the appropriate headers
        response = HttpResponse(file_content, content_type=content_type)
        response["Content-Length"] = os.path.getsize(cache_file_name)
        response["Content-Disposition"] = (
            "attachment; filename=%s" % f"{file_name}"
        )
        return response
    download = requests.get(apk.apk_url)
    if download.status_code != 200:
        return HttpResponse(
            {"message": "File not found."}, status=status.HTTP_404_NOT_FOUND
        )
    file_cache = open(cache_file_name, "wb")
    file_cache.write(download.content)
    file_cache.close()
    # Get the file's content type
    content_type, _ = mimetypes.guess_type(cache_file_name)
    # Read the file content into a variable
    with open(cache_file_name, "rb") as file:
        file_content = file.read()
    # Read the file content into a variable
    response = HttpResponse(file_content, content_type=content_type)
    response["Content-Length"] = os.path.getsize(cache_file_name)
    response["Content-Disposition"] = (
        "attachment; filename=%s" % f"{file_name}"
    )
    return response


@extend_schema(tags=["Mobile APK"], summary="Check APK Version")
@api_view(["GET"])
def check_apk_version(request, version, current_version):
    apk = MobileApk.objects.last()
    if not apk or apk.apk_version <= current_version:
        return Response(
            {"message": "No update found."}, status=status.HTTP_404_NOT_FOUND
        )
    return Response({"version": apk.apk_version}, status=status.HTTP_200_OK)


@extend_schema(
    request=inline_serializer(
        name="UploadAPKFile",
        fields={
            "apk_url": serializers.FileField(),
            "apk_version": serializers.CharField(),
            "secret": serializers.CharField(),
        },
    ),
    tags=["Mobile APK"],
    summary="Post APK File",
)
@api_view(["POST"])
def upload_apk_file(request, version):
    if request.data.get("secret") != APK_UPLOAD_SECRET:
        return Response(
            {"message": "Secret is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer = MobileApkSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    apk_version = serializer.validated_data.get("apk_version")
    download = requests.get(
        request.data.get("apk_url"), allow_redirects=True, stream=True
    )
    if download.status_code != 200:
        return HttpResponse(
            {"message": "File not found."}, status=status.HTTP_404_NOT_FOUND
        )
    filename = f"{APK_SHORT_NAME}-{apk_version}.apk"
    cache_file_name = os.path.join(apk_path, filename)
    file_cache = open(cache_file_name, "wb")
    file_cache.write(download.content)
    file_cache.close()
    storage.upload(
        cache_file_name, folder="apk",
        filename=f"{APK_SHORT_NAME}.apk"
    )
    serializer.save()
    return Response({"message": "ok"}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Mobile Assignment"])
class MobileAssignmentViewSet(ModelViewSet):
    serializer_class = MobileAssignmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination

    def get_queryset(self):
        user = self.request.user
        mobile_users = MobileAssignment.objects.prefetch_related(
            "administrations", "forms"
        ).filter(user=user)
        adm_q = Q()
        if user.is_superuser:
            adm = Administration.objects.filter(
                parent__isnull=True
            ).first()
            adm_q = Q(
                administrations__path__startswith=f"{adm.id}."
            )
        for ur in user.user_user_role.all():
            adm = ur.administration
            path = adm.path \
                if adm.path else f"{adm.id}."
            adm_q |= Q(administrations__path__startswith=path)
        if adm_q:
            descendant_users = MobileAssignment.objects.prefetch_related(
                "administrations", "forms"
            ).filter(adm_q)
            mobile_users |= descendant_users
        return mobile_users.order_by("-id").distinct()


@extend_schema(
    responses={
        (200, "application/json"): inline_serializer(
            "MobileDeviceDownloadDatapointListResponse",
            fields={
                "total": serializers.IntegerField(),
                "data": MobileDataPointDownloadListSerializer(many=True),
                "page": serializers.IntegerField(),
                "current": serializers.IntegerField(),
            },
        )
    },
    tags=["Mobile Device Form"],
    summary="GET Download List for Syncing Datapoints",
)
@api_view(["GET"])
@permission_classes([IsMobileAssignment])
def get_datapoint_download_list(request, version):
    assignment = cast(MobileAssignmentToken, request.auth).assignment
    forms = assignment.forms.values("id")
    administrations = [
        {"id": a.id, "path": a.path}
        for a in assignment.administrations.all()
    ]
    paginator = Pagination()

    # Start with base query for administration IDs
    admin_id_query = Q(
        administration_id__in=[a["id"] for a in administrations],
        form_id__in=forms,
    )
    # Build path query by combining conditions for all administration paths
    path_query = Q()
    for admin in administrations:
        adm_path = admin["path"] if admin["path"] else admin["id"]
        path_query |= Q(administration__path__startswith=adm_path)
    # Combine both queries with the form filter
    queryset = FormData.objects.filter(
        admin_id_query | (path_query & Q(form_id__in=forms))
    )
    if assignment.last_synced_at:
        queryset = queryset.filter(
            Q(created__gte=assignment.last_synced_at)
            | Q(updated__gte=assignment.last_synced_at)
        )

    queryset = queryset.filter(is_pending=False)
    queryset = queryset.values(
        "uuid",
        "id",
        "form_id",
        "name",
        "administration_id",
        "created",
        "updated",
    ).order_by("-created")

    instance = paginator.paginate_queryset(queryset, request)
    response = paginator.get_paginated_response(
        MobileDataPointDownloadListSerializer(instance, many=True).data
    )
    page = response.data["current"]
    total_page = response.data["total_page"]
    if page == total_page:
        assignment.last_synced_at = timezone.now()
        assignment.save()
    return response
