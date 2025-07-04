# Create your views here.
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    inline_serializer,
)

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q
from api.v1.v1_forms.models import (
    Forms,
)
from api.v1.v1_forms.serializers import (
    ListFormSerializer,
    WebFormDetailSerializer,
    FormDataSerializer,
    FormApproverRequestSerializer,
    FormApproverResponseSerializer,
)
from api.v1.v1_profile.models import (
    Administration,
    DataAccessTypes,
    UserRole,
)
from api.v1.v1_data.functions import get_cache, create_cache
from utils.custom_serializer_fields import validate_serializers_message


@extend_schema(
    responses={200: ListFormSerializer(many=True)},
    tags=["Form"],
    summary="To get list of forms",
    description="To get list of forms",
)
@api_view(["GET"])
def list_form(request, version):
    instance = Forms.objects.filter(parent__isnull=True).all()
    return Response(
        ListFormSerializer(instance=instance, many=True).data,
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses={200: WebFormDetailSerializer},
    tags=["Form"],
    summary="To get form in webform format",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def web_form_details(request, version, form_id):
    administration = Administration.objects.filter(
        parent__isnull=True,
    ).first()
    if not request.user.is_superuser:
        user_role = request.user.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first()
        if user_role:
            administration = user_role.administration
    cache_name = f"webform-{form_id}-{administration.id}"
    cache_data = get_cache(cache_name)
    if cache_data:
        return Response(cache_data, content_type="application/json;")
    instance = get_object_or_404(Forms, pk=form_id)
    instance = WebFormDetailSerializer(
        instance=instance, context={"user": request.user}
    ).data
    create_cache(cache_name, instance)
    return Response(instance, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: FormDataSerializer},
    tags=["Form"],
    summary="To get form data",
)
@api_view(["GET"])
def form_data(request, version, form_id):
    cache_name = f"form-{form_id}"
    cache_data = get_cache(cache_name)
    if cache_data:
        return Response(cache_data, content_type="application/json;")
    instance = get_object_or_404(Forms, pk=form_id)
    instance = FormDataSerializer(instance=instance).data
    create_cache(cache_name, instance)
    return Response(instance, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="administration_id",
            required=True,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="form_id",
            required=True,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={200: FormApproverResponseSerializer(many=True)},
    tags=["Form"],
    summary="To get approver user list",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def form_approver(request, version):
    serializer = FormApproverRequestSerializer(data=request.GET)
    if not serializer.is_valid():
        return Response(
            {"message": validate_serializers_message(serializer.errors)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    adm = serializer.validated_data.get("administration_id")
    path = adm.path if adm.path else f"{adm.id}."
    instance = Administration.objects.filter(
        path__startswith=path,
    )
    ancestors = list(adm.ancestors.all()) if adm.ancestors else []
    instance = ancestors + [
        serializer.validated_data.get("administration_id")
    ] + list(instance)
    return Response(
        FormApproverResponseSerializer(
            instance=instance,
            many=True,
            context={"form": serializer.validated_data.get("form_id")},
        ).data,
        status=status.HTTP_200_OK,
    )


@extend_schema(
    responses={
        (200, "application/json"): inline_serializer(
            "CheckFormApproverSerializer",
            fields={
                "count": serializers.IntegerField(),
            },
        )
    },
    tags=["Form"],
    summary="To check approver for defined form_id & logged in user",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_form_approver(request, form_id, version):
    form = get_object_or_404(Forms, pk=form_id)
    # Check if the user has any roles that allow them to approve the form
    # This will include checking the user's administration and its ancestors
    by_ancestors = Q()
    for ur in request.user.user_user_role.all():
        adm = ur.administration
        if adm.ancestors:
            ancestors = list(adm.ancestors.all()) + [adm]
            by_ancestors |= Q(administration__in=ancestors)
    approver = UserRole.objects.filter(
        by_ancestors,
        user__user_form__form=form,
        role__role_role_access__data_access=DataAccessTypes.approve,
    ).count()
    return Response({"count": approver}, status=status.HTTP_200_OK)
