from math import ceil
# from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_approval.models import (
    DataBatch,
)
from api.v1.v1_approval.serializers import (
    ApproveDataRequestSerializer,
    ListBatchSerializer,
    CreateBatchSerializer,
    ListDataBatchSerializer,
    ListPendingFormDataSerializer,
    BatchDataFilterSerializer,
    ListBatchSummarySerializer,
    ListBatchCommentSerializer,
    BatchListRequestSerializer,
)
from api.v1.v1_forms.constants import (
    QuestionTypes
)
from api.v1.v1_forms.models import Questions
from api.v1.v1_users.models import SystemUser
from api.v1.v1_data.models import Answers
from mis.settings import REST_FRAMEWORK
from utils.custom_permissions import (
    IsSuperAdmin,
    IsSubmitter,
    IsApprover,
)
from api.v1.v1_profile.constants import DataAccessTypes
from utils.custom_serializer_fields import validate_serializers_message
from utils.default_serializers import DefaultResponseSerializer

period_length = 60 * 15


@extend_schema(
    responses={
        (200, "application/json"): inline_serializer(
            "DataBatchResponse",
            fields={
                "current": serializers.IntegerField(),
                "total": serializers.IntegerField(),
                "total_page": serializers.IntegerField(),
                "batch": ListDataBatchSerializer(many=True),
            },
        )
    },
    tags=["Pending Data"],
    parameters=[
        OpenApiParameter(
            name="page",
            required=True,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="approved",
            required=False,
            default=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="subordinate",
            required=False,
            default=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
        ),
    ],
    summary="To get list of pending batch",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsApprover])
def list_pending_batch(request, version):
    serializer = BatchDataFilterSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response(
            {"message": validate_serializers_message(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user: SystemUser = request.user
    page_size = REST_FRAMEWORK.get("PAGE_SIZE")

    subordinate = serializer.validated_data.get("subordinate")
    approved = serializer.validated_data.get("approved")
    user_role = user.user_user_role.filter(
        role__role_role_access__data_access=DataAccessTypes.approve
    ).first()
    data_approval = user.data_approval_user.filter(
        batch__approved=approved,
        role=user_role.role,
    ).all()
    batch_ids = [
        d.batch.id for d in data_approval
    ]
    queryset = DataBatch.objects.filter(
        id__in=batch_ids,
    ).order_by("-created")

    next_level = user_role.administration.level.level + 1 \
        if user_role else None
    if subordinate and next_level:
        queryset = queryset.filter(
            batch_approval__administration__level__level=next_level,
        )
    paginator = PageNumberPagination()
    paginator.paginate_queryset(queryset, request)
    total = queryset.count()

    data = {
        "current": int(request.GET.get("page", "1")),
        "total": total,
        "total_page": ceil(total / page_size),
        "batch": ListDataBatchSerializer(
            instance=queryset,
            context={
                "user": user,
                "approved": approved,
                "subordinate": subordinate,
                "user_role": user_role,
            },
            many=True,
        ).data,
    }
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: ListPendingFormDataSerializer(many=True)},
    tags=["Pending Data"],
    summary="To get list of pending data by batch",
)
@api_view(["GET"])
@permission_classes(
    [IsAuthenticated, IsSuperAdmin | IsSubmitter | IsApprover]
)
def list_data_batch(request, version, batch_id):
    batch = get_object_or_404(DataBatch, pk=batch_id)
    batch_list = batch.batch_data_list.filter(
        batch__approved=False,
        data__is_pending=True,
    ).order_by("-created")
    data = [
        d.data for d in batch_list
    ]
    return Response(
        ListPendingFormDataSerializer(
            instance=data,
            many=True
        ).data,
        status=status.HTTP_200_OK,
    )


@extend_schema(
    request=ApproveDataRequestSerializer(),
    responses={200: DefaultResponseSerializer},
    tags=["Pending Data"],
    summary="Approve pending data",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsApprover | IsSubmitter | IsSuperAdmin])
def approve_pending_data(request, version):
    serializer = ApproveDataRequestSerializer(
        data=request.data, context={"user": request.user}
    )
    if not serializer.is_valid():
        return Response(
            {"message": validate_serializers_message(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response({"message": "Ok"}, status=status.HTTP_200_OK)


class BatchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            (200, "application/json"): inline_serializer(
                "ListDataBatchResponse",
                fields={
                    "current": serializers.IntegerField(),
                    "total": serializers.IntegerField(),
                    "total_page": serializers.IntegerField(),
                    "data": ListBatchSerializer(many=True),
                },
            )
        },
        tags=["Pending Data"],
        summary="To get list of batch",
        parameters=[
            OpenApiParameter(
                name="page",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="form",
                required=False,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="approved",
                default=False,
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request, version):
        serializer = BatchListRequestSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(
                {"message": validate_serializers_message(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = DataBatch.objects.filter(
            user=request.user,
            approved=serializer.validated_data.get("approved"),
        ).order_by("-id")
        form_id = serializer.validated_data.get("form")
        if form_id:
            queryset = queryset.filter(form_id=form_id)
        paginator = PageNumberPagination()
        instance = paginator.paginate_queryset(queryset, request)
        page_size = REST_FRAMEWORK.get("PAGE_SIZE")
        data = {
            "current": int(request.GET.get("page", "1")),
            "total": queryset.count(),
            "total_page": ceil(queryset.count() / page_size),
            "data": ListBatchSerializer(instance=instance, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateBatchSerializer(),
        tags=["Pending Data"],
        summary="To create batch",
    )
    def post(self, request, version):
        serializer = CreateBatchSerializer(
            data=request.data, context={"user": request.user}
        )
        if not serializer.is_valid():
            return Response(
                {"detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=request.user)
        return Response(
            {
                "message": "Batch created successfully",
            },
            status=status.HTTP_201_CREATED
        )


class BatchSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ListBatchSummarySerializer(many=True)},
        tags=["Pending Data"],
        summary="To get batch summary",
    )
    def get(self, request, batch_id, version):
        batch = get_object_or_404(DataBatch, pk=batch_id)
        # Get questions for option and multiple_option types
        questions = Questions.objects.filter(
            type__in=[
                QuestionTypes.option,
                QuestionTypes.multiple_option,
            ]
        )
        # Get all answers for these questions in the batch
        answers = Answers.objects.filter(
            data__data_batch_list__batch=batch,
            data__is_pending=True,
            question__in=questions,
        ).distinct("question")
        return Response(
            ListBatchSummarySerializer(
                instance=answers, many=True, context={"batch": batch}
            ).data,
            status=status.HTTP_200_OK,
        )


class BatchCommentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ListBatchCommentSerializer(many=True)},
        tags=["Pending Data"],
        summary="To get batch comment",
    )
    def get(self, request, batch_id, version):
        batch = get_object_or_404(DataBatch, pk=batch_id)
        instance = batch.batch_batch_comment.all().order_by("-id")
        return Response(
            ListBatchCommentSerializer(instance=instance, many=True).data,
            status=status.HTTP_200_OK,
        )
