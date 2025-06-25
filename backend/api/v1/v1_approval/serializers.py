from django.db.models import Sum, Count, Q, F
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django_q.tasks import async_task

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_approval.models import (
    DataApproval,
    DataBatch,
    DataBatchList,
    DataBatchComments,
)
from api.v1.v1_data.models import FormData
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
    CustomFileField,
)
from utils.default_serializers import CommonDataSerializer
from utils.email_helper import send_email, EmailTypes
from utils.functions import update_date_time_format
from mis.settings import APP_NAME
from utils import storage


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


class PendingBatchApproverSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name")
    administration_level = serializers.CharField(
        source="administration.level.level"
    )
    status_text = serializers.SerializerMethodField()
    allow_approve = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_status_text(self, instance: DataApproval):
        return DataApprovalStatus.FieldStr.get(instance.status)

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_allow_approve(self, instance: DataApproval):
        user: SystemUser = self.context.get("user")
        if instance.status == DataApprovalStatus.pending:
            # Check if the user is the approver
            return instance.user == user
        return False

    class Meta:
        model = DataApproval
        fields = [
            "id",
            "name",
            "administration_level",
            "status",
            "status_text",
            "allow_approve",
        ]


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

    @extend_schema_field(PendingBatchApproverSerializer(many=True))
    def get_approver(self, instance: DataBatch):
        user: SystemUser = self.context.get("user")
        approved: bool = self.context.get("approved")
        subordinate: bool = self.context.get("subordinate", False)
        approval_status = DataApprovalStatus.pending
        if approved:
            approval_status = DataApprovalStatus.approved
        # Get my approval
        my_approval = instance.batch_approval.filter(
            user=user,
            status=approval_status,
        ).first()
        next_level = my_approval.administration.level.level + 1
        approvers = instance.batch_approval.filter(
            administration__level__level__lt=next_level,
            status=DataApprovalStatus.pending,
        ).order_by(
            "administration__level__level"
        ).all()
        # Get all approvers grouped by administration level
        if approval_status == DataApprovalStatus.pending:
            # For pending status, check if all approvers at a level are pending
            # Get levels where all approvers are pending
            adm_levels_with_all_pending = instance.batch_approval.values(
                'administration__level__level'
            ).annotate(
                total=Count('id'),
                pending=Count(
                    'id', filter=Q(status=DataApprovalStatus.pending)
                )
            ).filter(
                # Only include levels where all approvers are pending
                total=F('pending'),
                administration__level__level__gte=next_level
            ).values_list('administration__level__level', flat=True)
            # Get approvers from those levels where all are pending
            approvers = instance.batch_approval.filter(
                administration__level__level__in=adm_levels_with_all_pending,
                status=DataApprovalStatus.pending
            ).order_by(
                "-administration__level__level"
            ).all()
        if subordinate:
            approvers = instance.batch_approval.filter(
                administration__level__level=next_level,
                status=DataApprovalStatus.pending,
            ).all()
        if approvers.count() == 0 and not approved:
            approvers = [my_approval]
        return PendingBatchApproverSerializer(
            approvers,
            many=True,
            context={"user": user}
        ).data

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
    approval = CustomPrimaryKeyRelatedField(
        queryset=DataApproval.objects.none()
    )
    status = CustomChoiceField(
        choices=[DataApprovalStatus.approved, DataApprovalStatus.rejected]
    )
    comment = CustomCharField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        user: SystemUser = self.context.get("user")
        self.fields.get("approval").queryset = DataApproval.objects.filter(
            user=user,
            status=DataApprovalStatus.pending,
        ).select_related("batch", "administration", "role")

    def create(self, validated_data):
        approval = validated_data.get("approval")
        status = validated_data.get("status")
        comment = validated_data.pop("comment", None)
        user: SystemUser = self.context.get("user")
        # Update the status of the approval
        approval.status = status
        approval.save()

        # Add comment if provided
        if comment:
            DataBatchComments.objects.create(
                user=user,
                batch=approval.batch,
                comment=comment
            )
        # Get the batch and get all pending data for this batch
        batch = approval.batch
        pending_data = batch.batch_data_list.filter(
            data__is_pending=True,
        ).select_related("data__created_by", "data__form")
        # Get all data submitted by the user
        submitter_emails = pending_data.values_list(
            "data__created_by__email", flat=True
        ).distinct()
        # Get total number of records
        data_count = pending_data.count()
        data = {
            "send_to": submitter_emails,
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
            # Send to lower level approvers
            adm_level = approval.administration.level.level
            lower_approvers = batch.batch_approval.filter(
                administration__level__level__gt=adm_level,
            )
            if lower_approvers.exists():
                lower_emails = [
                    approver.user.email for approver in lower_approvers
                ]
                inform_data = {
                    "send_to": lower_emails,
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
        # Check if all administration levels have at least one approval
        # Get all unique administration levels for this batch
        adm_levels_with_status = batch.batch_approval.values(
            'administration__level__level'
        ).annotate(
            total=Count('id'),
            approved=Count(
                'id', filter=Q(status=DataApprovalStatus.approved)
            )
        )

        # Check if each administration level has at least one approval
        all_levels_have_approval = all(
            level_data['approved'] > 0
            for level_data in adm_levels_with_status
        )
        # If all levels have
        if all_levels_have_approval:
            # Seed data via Async Task
            for dl in batch.batch_data_list.filter(
                data__is_pending=True,
            ).all():
                data = dl.data
                async_task("api.v1.v1_data.tasks.seed_approved_data", data)
            batch.approved = True
            batch.updated = timezone.now()
            batch.save()
        return approval

    def update(self, instance, validated_data):
        pass

    class Meta:
        fields = ["approval", "status", "comment"]


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
            "administration__level__level"
        ).all()
        for approver in approvers:
            data.append(
                {
                    "name": approver.user.get_full_name(),
                    "administration": approver.administration.name,
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
                data__data_batch_list__batch=batch,
                data__is_pending=True,
                question_id=instance.question.id
            ).aggregate(Sum("value"))
            return val.get("value__sum")
        elif instance.question.type == QuestionTypes.administration:
            return (
                Answers.objects.filter(
                    data__data_batch_list__batch=batch,
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
                    data__data_batch_list__batch=batch,
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
    )
    files = CustomListField(
        child=CustomFileField(),
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
        for item in data:
            # Check if the data item has approval
            if not item.has_approval:
                raise ValidationError(
                    "One or more data items do not have approval."
                )
            # Check if the data item is pending
            if not item.is_pending:
                raise ValidationError(
                    "One or more data items are not pending."
                )
            # Check if the data item was created by the user
            if item.created_by != self.context.get("user"):
                raise ValidationError(
                    "One or more data items were not submitted by the user."
                )
        return data

    def validate_files(self, files):
        allowed_formats = ["csv", "xls", "xlsx", "docx", "doc", "pdf"]
        for file in files:
            file_extension = file.name.split(".")[-1].lower()
            if file_extension not in allowed_formats:
                raise ValidationError(
                    f"Invalid file format for {file.name}."
                    f"Allowed formats are: {', '.join(allowed_formats)}"
                )
        return files

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
            raise ValidationError({
                "data": (
                    "All data must belong to the same administration."
                )
            })
        return attrs

    def create(self, validated_data):
        form_id = validated_data.get("data")[0].form_id
        user: SystemUser = validated_data.get("user")
        user_role = user.user_user_role.filter(
            role__role_role_access__data_access=DataAccessTypes.submit
        ).first()
        if not user_role:
            raise ValidationError({
                "detail": (
                    "User does not have permission to create a batch."
                )
            })
        # try:
        with transaction.atomic():
            obj = DataBatch.objects.create(
                form_id=form_id,
                administration=user_role.administration,
                user=user,
                name=validated_data.get("name"),
            )
            # Create batch data list entries
            try:
                for data in validated_data.get("data"):
                    DataBatchList.objects.create(batch=obj, data=data)
            except Exception as e:
                raise ValidationError({
                    "detail": f"Failed to create batch data list: {str(e)}"
                })
            # Send email to approvers
            try:
                emails = [
                    approver["user"].email for approver in obj.approvers()
                ]
                if len(emails):
                    number_of_records = obj.batch_data_list.count()
                    data = {
                        "send_to": emails,
                        "listing": [
                            {"name": "Batch Name", "value": obj.name},
                            {
                                "name": "Questionnaire",
                                "value": obj.form.name
                            },
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
                    send_email(
                        context=data,
                        type=EmailTypes.pending_approval
                    )
                    # Create DataApproval for each approver
                    for approver in obj.approvers():
                        DataApproval.objects.create(
                            batch=obj,
                            administration=approver["administration"],
                            role=approver["role"],
                            user=approver["user"],
                            status=DataApprovalStatus.pending,
                        )
            except Exception as e:
                raise ValidationError({
                    "detail": (
                        f"Failed to send email to approvers: {str(e)}"
                    )
                })

            # Add comment if provided
            if validated_data.get("comment"):
                try:
                    DataBatchComments.objects.create(
                        user=user,
                        batch=obj,
                        comment=validated_data.get("comment")
                    )
                except Exception as e:
                    raise ValidationError({
                        "detail": (
                            f"Failed to add comment: {str(e)}"
                        )
                    })
            # Handle file uploads
            if validated_data.get("files"):
                fs = FileSystemStorage()
                for f in validated_data.get("files"):
                    try:
                        file = fs.save(
                            f"./tmp/{f.name}",
                            f,
                        )
                        file_path = fs.path(file)
                        # Save the file to storage
                        file_path = storage.upload(
                            file=file_path,
                            filename=f.name,
                            folder="batch_attachments"
                        )
                        obj.batch_batch_attachment.create(
                            file_path=file_path
                        )
                        DataBatchComments.objects.create(
                            batch=obj,
                            user=self.context['user'],
                            comment=f"File uploaded: {f.name}",
                            file_path=file_path,
                        )
                    except Exception as e:
                        raise ValidationError({
                            "detail": (
                                f"Failed to upload file {f.name}: {str(e)}"
                            )
                        })
        return obj
        # except ValidationError as ve:
        #     # Let validation errors pass through with their messages
        #     raise ve
        # except Exception as e:
        #     # Catch any other unexpected errors
        #     raise ValidationError(f"Failed to create batch: {str(e)}")
