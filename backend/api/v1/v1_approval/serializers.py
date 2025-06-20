from django.db.models import Sum
from django.utils import timezone
from django_q.tasks import async_task

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_approval.models import (
    FormData,
    DataApproval,
    DataBatch,
    DataBatchComments,
)
from api.v1.v1_data.models import Answers, AnswerHistory
from api.v1.v1_forms.constants import QuestionTypes
from api.v1.v1_forms.models import (
    Forms,
)
from api.v1.v1_profile.models import (
    DataAccessTypes,
)
from api.v1.v1_users.models import SystemUser
from utils.custom_serializer_fields import (
    CustomPrimaryKeyRelatedField,
    CustomListField,
    CustomCharField,
    CustomChoiceField,
    CustomBooleanField,
)
from utils.default_serializers import CommonDataSerializer
from utils.email_helper import send_email, EmailTypes
from utils.functions import update_date_time_format
from mis.settings import APP_NAME


class ListFormDataSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    administration = serializers.SerializerMethodField()
    pending_data = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_created_by(self, instance: FormData):
        return instance.created_by.get_full_name()

    @extend_schema_field(OpenApiTypes.STR)
    def get_updated_by(self, instance: FormData):
        if instance.updated_by:
            return instance.updated_by.get_full_name()
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_created(self, instance: FormData):
        return update_date_time_format(instance.created)

    @extend_schema_field(OpenApiTypes.STR)
    def get_updated(self, instance: FormData):
        return update_date_time_format(instance.updated)

    @extend_schema_field(
        inline_serializer(
            "HasPendingData",
            fields={
                "id": serializers.IntegerField(),
                "created_by": serializers.CharField(),
            },
        )
    )
    def get_pending_data(self, instance: FormData):
        # Check if there's a pending version of this data point
        batch = None
        pending_data = FormData.objects.select_related(
            "created_by"
        ).filter(uuid=instance.uuid, is_pending=True).first()
        if pending_data:
            batch = DataBatch.objects.filter(
                pk=pending_data.batch_id
            ).first()
        if pending_data and (not batch or not batch.approved):
            return {
                "id": pending_data.id,
                "created_by": pending_data.created_by.get_full_name(),
            }
        return None

    def get_administration(self, instance: FormData):
        return " - ".join(instance.administration.full_name.split("-")[1:])

    class Meta:
        model = FormData
        fields = [
            "id",
            "uuid",
            "name",
            "form",
            "administration",
            "geo",
            "created_by",
            "updated_by",
            "created",
            "updated",
            "pending_data",
            "submitter",
        ]


class BatchDataFilterSerializer(serializers.Serializer):
    approved = CustomBooleanField(default=False)
    subordinate = CustomBooleanField(default=False)


class ListDataBatchSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()
    form = serializers.SerializerMethodField()
    administration = serializers.SerializerMethodField()
    total_data = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_created_by(self, instance: DataBatch):
        return instance.user.get_full_name()

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_data(self, instance: DataBatch):
        return instance.batch_data_list.count()

    @extend_schema_field(CommonDataSerializer)
    def get_form(self, instance: DataBatch):
        return {
            "id": instance.form.id,
            "name": instance.form.name,
            "approval_instructions": instance.form.approval_instructions,
        }

    @extend_schema_field(CommonDataSerializer)
    def get_administration(self, instance: DataBatch):
        return {
            "id": instance.administration_id,
            "name": instance.administration.name,
        }

    @extend_schema_field(OpenApiTypes.STR)
    def get_created(self, instance: DataBatch):
        return update_date_time_format(instance.created)

    @extend_schema_field(
        inline_serializer(
            "PendingBatchApprover",
            fields={
                "id": serializers.IntegerField(),
                "name": serializers.CharField(),
                "status": serializers.IntegerField(),
                "status_text": serializers.CharField(),
                "allow_approve": serializers.BooleanField(),
            },
        )
    )
    def get_approver(self, instance: DataBatch):
        user: SystemUser = self.context.get("user")
        approved: bool = self.context.get("approved")
        user_role = user.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first()
        next_level = (
            user_role.administration.level.level - 1
            if approved
            else user_role.administration.level.level + 1
        )
        approvers = instance.approvers(adm_level=next_level)
        if not approvers:
            return {
                "id": None,
                "name": None,
                "status": DataApprovalStatus.pending,
                "status_text": DataApprovalStatus.FieldStr.get(
                    DataApprovalStatus.pending
                ),
                "allow_approve": False,
            }
        approver = approvers[0]
        return {
            "id": approver.id,
            "name": approver.user.get_full_name(),
            "status": approver.status,
            "status_text": DataApprovalStatus.FieldStr.get(approver.status),
            "allow_approve": (
                approver.status == DataApprovalStatus.pending
                and user_role.administration_id == instance.administration_id
            ),
        }

    class Meta:
        model = DataBatch
        fields = [
            "id",
            "name",
            "form",
            "administration",
            "created_by",
            "created",
            "approver",
            "approved",
            "total_data",
        ]


class ListPendingFormDataSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    administration = serializers.ReadOnlyField(source="administration.name")
    answer_history = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_created_by(self, instance: FormData):
        return instance.created_by.get_full_name()

    @extend_schema_field(OpenApiTypes.STR)
    def get_created(self, instance: FormData):
        return update_date_time_format(instance.created)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_answer_history(self, instance: FormData):
        # Check for history in answer_history table
        history = AnswerHistory.objects.filter(
            data=instance
        ).count()
        return True if history > 0 else False

    class Meta:
        model = FormData
        fields = [
            "id",
            "uuid",
            "name",
            "form",
            "administration",
            "geo",
            "submitter",
            "duration",
            "created_by",
            "created",
            "answer_history",
        ]


class ApproveDataRequestSerializer(serializers.Serializer):
    batch = CustomPrimaryKeyRelatedField(
        queryset=DataBatch.objects.none()
    )
    status = CustomChoiceField(
        choices=[DataApprovalStatus.approved, DataApprovalStatus.rejected]
    )
    comment = CustomCharField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        user: SystemUser = self.context.get("user")
        if user:
            self.fields.get(
                "batch"
            ).queryset = DataBatch.objects.filter(
                batch_approval__user=user, approved=False
            )

    def create(self, validated_data):
        batch: DataBatch = validated_data.get("batch")
        user = self.context.get("user")
        comment = validated_data.get("comment")
        user_level = user.user_user_role.administration.level
        approval = DataApproval.objects.get(user=user, batch=batch)
        approval.status = validated_data.get("status")
        approval.save()
        # Get the first form data in the batch to get submitter email
        first_data = FormData.objects.filter(
            batch=batch, is_pending=True
        ).first()
        data_count = FormData.objects.filter(
            batch=batch, is_pending=True
        ).count()
        data = {
            "send_to": [first_data.created_by.email],
            "batch": batch,
            "user": user,
        }
        listing = [
            {
                "name": "Batch Name",
                "value": batch.name,
            },
            {
                "name": "Number of Records",
                "value": data_count,
            },
            {
                "name": "Questionnaire",
                "value": batch.form.name,
            },
        ]
        if approval.status == DataApprovalStatus.approved:
            listing.append(
                {
                    "name": "Approver",
                    "value": f"{user.name}",
                }
            )
            if comment:
                listing.append({"name": "Comment", "value": comment})
            data.update(
                {
                    "listing": listing,
                    "extend_body": (
                        "Further approvals may be required "
                        "before data is finalised."
                        "You can also track your data approval in the "
                        f"{APP_NAME} platform "
                        "[Data > Manage Submissions > Pending Approval]"
                    ),
                }
            )
            send_email(context=data, type=EmailTypes.batch_approval)
        else:
            listing.append(
                {
                    "name": "Rejector",
                    "value": f"{user.name}",
                }
            )
            if comment:
                listing.append({"name": "Comment", "value": comment})
            # rejection request change to user
            data.update(
                {
                    "listing": listing,
                    "extend_body": (
                        "You can also access the rejected data "
                        f"in the {APP_NAME} platform "
                        "[My Profile > Data uploads > Rejected]"
                    ),
                }
            )
            send_email(context=data, type=EmailTypes.batch_rejection)
            # send email to lower approval
            lower_approvals = DataApproval.objects.filter(
                batch=batch, level__level__gt=user_level.level
            ).all()
            # filter --> send email only to lower approval
            lower_approval_user_ids = [u.user_id for u in lower_approvals]
            lower_approval_users = SystemUser.objects.filter(
                id__in=lower_approval_user_ids, deleted_at=None
            ).all()
            lower_approval_emails = [
                u.email for u in lower_approval_users if u.email != user.email
            ]
            if lower_approval_emails:
                inform_data = {
                    "send_to": lower_approval_emails,
                    "listing": listing,
                    "extend_body": """
                    The data submitter has also been notified.
                    They can modify the data and submit again for approval
                    """,
                }
                send_email(
                    context=inform_data,
                    type=EmailTypes.inform_batch_rejection_approver,
                )
        if validated_data.get("comment"):
            DataBatchComments.objects.create(
                user=user, batch=batch, comment=validated_data.get("comment")
            )
        if not DataApproval.objects.filter(
            batch=batch,
            status__in=[
                DataApprovalStatus.pending,
                DataApprovalStatus.rejected,
            ],
        ).count():
            # Get all pending data for this batch
            form_data_list = FormData.objects.filter(
                batch=batch, is_pending=True
            ).all()
            # Seed data via Async Task
            for data in form_data_list:
                async_task("api.v1.v1_data.tasks.seed_approved_data", data)
            batch.approved = True
            batch.updated = timezone.now()
            batch.save()
        return object

    def update(self, instance, validated_data):
        pass


class ListBatchSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    administration = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    total_data = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField(source="approved")
    approvers = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()

    @extend_schema_field(CommonDataSerializer)
    def get_form(self, instance: DataBatch):
        return {
            "id": instance.form.id,
            "name": instance.form.name,
            "approval_instructions": instance.form.approval_instructions,
        }

    @extend_schema_field(CommonDataSerializer)
    def get_administration(self, instance: DataBatch):
        return {
            "id": instance.administration_id,
            "name": instance.administration.name,
        }

    @extend_schema_field(
        inline_serializer(
            "BatchFile",
            fields={
                "name": serializers.CharField(),
                "file": serializers.URLField(),
            },
        )
    )
    def get_file(self, instance: DataBatch):
        if instance.file:
            path = instance.file
            first_pos = path.rfind("/")
            last_pos = len(path)
            return {
                "name": path[first_pos + 1: last_pos],
                "file": instance.file,
            }
        return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_data(self, instance: DataBatch):
        return instance.batch_data_list.all().count()

    @extend_schema_field(
        inline_serializer(
            "BatchApprover",
            fields={
                "name": serializers.CharField(),
                "administration": serializers.CharField(),
                "status": serializers.IntegerField(),
                "status_text": serializers.CharField(),
            },
            many=True,
        )
    )
    def get_approvers(self, instance: DataBatch):
        data = []
        approvers = instance.batch_approval.order_by(
            "level"
        ).all()
        for approver in approvers:
            approver_adm = approver.user.user_user_role.administration
            data.append(
                {
                    "name": approver.user.get_full_name(),
                    "administration": approver_adm.name,
                    "status": approver.status,
                    "status_text": DataApprovalStatus.FieldStr.get(
                        approver.status
                    ),
                }
            )
        return data

    @extend_schema_field(OpenApiTypes.DATE)
    def get_created(self, instance):
        return update_date_time_format(instance.created)

    @extend_schema_field(OpenApiTypes.DATE)
    def get_updated(self, instance):
        return update_date_time_format(instance.updated)

    class Meta:
        model = DataBatch
        fields = [
            "id",
            "name",
            "form",
            "administration",
            "file",
            "total_data",
            "created",
            "updated",
            "status",
            "approvers",
        ]


class ListBatchSummarySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="question.id")
    question = serializers.ReadOnlyField(source="question.label")
    type = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    @extend_schema_field(
        CustomChoiceField(
            choices=[QuestionTypes.FieldStr[d] for d in QuestionTypes.FieldStr]
        )
    )
    def get_type(self, instance):
        return QuestionTypes.FieldStr.get(instance.question.type)

    @extend_schema_field(OpenApiTypes.ANY)
    def get_value(self, instance):
        batch = self.context.get("batch")
        if instance.question.type == QuestionTypes.number:
            val = Answers.objects.filter(
                data__batch=batch,
                data__is_pending=True,
                question_id=instance.question.id
            ).aggregate(Sum("value"))
            return val.get("value__sum")
        elif instance.question.type == QuestionTypes.administration:
            return (
                Answers.objects.filter(
                    data__batch=batch,
                    data__is_pending=True,
                    question_id=instance.question.id
                )
                .distinct("value")
                .count()
            )
        else:
            data = []
            for option in instance.question.options.all():
                val = Answers.objects.filter(
                    data__batch=batch,
                    data__is_pending=True,
                    question_id=instance.question.id,
                    options__contains=option.value,
                ).count()
                data.append({"type": option.label, "total": val})
            return data

    class Meta:
        model = Answers
        fields = ["id", "question", "type", "value"]


class ListBatchCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    @extend_schema_field(
        inline_serializer(
            "BatchUserComment",
            fields={
                "name": serializers.CharField(),
                "email": serializers.CharField(),
            },
        )
    )
    def get_user(self, instance: DataBatchComments):
        return {
            "name": instance.user.get_full_name(),
            "email": instance.user.email,
        }

    @extend_schema_field(OpenApiTypes.DATE)
    def get_created(self, instance: DataBatchComments):
        return update_date_time_format(instance.created)

    class Meta:
        model = DataBatchComments
        fields = ["user", "comment", "created"]


class BatchListRequestSerializer(serializers.Serializer):
    approved = CustomBooleanField(default=False)
    form = CustomPrimaryKeyRelatedField(
        queryset=Forms.objects.filter(parent__isnull=True).all(),
        required=False
    )


class CreateBatchSerializer(serializers.Serializer):
    name = CustomCharField()
    comment = CustomCharField(required=False)
    data = CustomListField(
        child=CustomPrimaryKeyRelatedField(
            queryset=FormData.objects.none()
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get("data").child.queryset = FormData.objects.filter(
            is_pending=True
        )

    def validate_name(self, name):
        if DataBatch.objects.filter(name__iexact=name).exists():
            raise ValidationError("name has already been taken")
        return name

    def validate_data(self, data):
        if len(data) == 0:
            raise ValidationError("No data found for this batch")
        return data

    def validate(self, attrs):
        if len(attrs.get("data")) == 0:
            raise ValidationError(
                {"data": "No form found for this batch"}
            )
        form = attrs.get("data")[0].form
        for pending in attrs.get("data"):
            if pending.form_id != form.id:
                raise ValidationError({
                    "data": (
                        "Mismatched form ID for one or more"
                        " pending data items."
                    )
                })
        # Check if data has different administrations
        administrations = set(
            data.administration_id for data in attrs.get("data")
        )
        if len(administrations) > 1:
            raise ValidationError(
                "All data must belong to the same administration."
            )
        return attrs

    def create(self, validated_data):
        form_id = validated_data.get("data")[0].form_id
        user: SystemUser = validated_data.get("user")
        user_role = user.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first()
        obj = DataBatch.objects.create(
            form_id=form_id,
            administration=user_role.administration,
            user=user,
            name=validated_data.get("name"),
        )
        for data in validated_data.get("data"):
            obj.batch_data_list.add(data)
        if obj.approvers:
            # Send email to all approvers
            emails = [
                approver.user.email for approver in obj.approvers
            ]
            number_of_records = obj.batch_data_list.count()
            data = {
                "send_to": emails,
                "listing": [
                    {"name": "Batch Name", "value": obj.name},
                    {"name": "Questionnaire", "value": obj.form.name},
                    {
                        "name": "Number of Records",
                        "value": number_of_records,
                    },
                    {
                        "name": "Submitter",
                        "value": f"""{obj.user.name}""",
                    },
                ],
            }
            send_email(context=data, type=EmailTypes.pending_approval)

        if validated_data.get("comment"):
            DataBatchComments.objects.create(
                user=user, batch=obj, comment=validated_data.get("comment")
            )
        return obj
