import requests
from django.db.models import Q
from django.utils import timezone

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.v1_data.models import (
    FormData,
    Answers,
    AnswerHistory,
)
from api.v1.v1_forms.constants import QuestionTypes
from api.v1.v1_forms.models import (
    Questions,
)
from api.v1.v1_profile.models import Administration, EntityData
from api.v1.v1_users.models import Organisation
from utils.custom_serializer_fields import (
    CustomPrimaryKeyRelatedField,
    UnvalidatedField,
    CustomListField,
    CustomCharField,
    CustomIntegerField,
)
from utils.functions import update_date_time_format, get_answer_value
from utils.functions import get_answer_history


class SubmitFormDataSerializer(serializers.ModelSerializer):
    administration = CustomPrimaryKeyRelatedField(
        queryset=Administration.objects.none()
    )
    name = CustomCharField()
    geo = CustomListField(required=False, allow_null=True)
    submitter = CustomCharField(required=False)
    duration = CustomIntegerField(required=False)
    uuid = serializers.CharField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get(
            "administration"
        ).queryset = Administration.objects.all()

    class Meta:
        model = FormData
        fields = [
            "name",
            "geo",
            "administration",
            "submitter",
            "duration",
            "uuid",
        ]


class SubmitFormDataAnswerSerializer(serializers.ModelSerializer):
    value = UnvalidatedField(allow_null=False)
    question = CustomPrimaryKeyRelatedField(queryset=Questions.objects.none())
    index = CustomIntegerField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get("question").queryset = Questions.objects.all()

    def validate_value(self, value):
        return value

    def validate(self, attrs):
        if attrs.get("value") == "":
            raise ValidationError(
                "Value is required for Question:{0}".format(
                    attrs.get("question").id
                )
            )

        if (
            isinstance(attrs.get("value"), list)
            and len(attrs.get("value")) == 0
        ):
            raise ValidationError(
                "Value is required for Question:{0}".format(
                    attrs.get("question").id
                )
            )

        if not isinstance(attrs.get("value"), list) and attrs.get(
            "question"
        ).type in [
            QuestionTypes.geo,
            QuestionTypes.option,
            QuestionTypes.multiple_option,
        ]:
            raise ValidationError(
                "Valid list value is required for Question:{0}".format(
                    attrs.get("question").id
                )
            )
        elif not isinstance(attrs.get("value"), str) and attrs.get(
            "question"
        ).type in [
            QuestionTypes.text,
            QuestionTypes.photo,
            QuestionTypes.date,
            QuestionTypes.attachment,
            QuestionTypes.signature,
        ]:
            raise ValidationError(
                "Valid string value is required for Question:{0}".format(
                    attrs.get("question").id
                )
            )
        elif not (
            isinstance(attrs.get("value"), int)
            or isinstance(attrs.get("value"), float)
        ) and attrs.get("question").type in [
            QuestionTypes.number,
            QuestionTypes.administration,
            QuestionTypes.cascade,
        ]:
            raise ValidationError(
                "Valid number value is required for Question:{0}".format(
                    attrs.get("question").id
                )
            )

        if attrs.get("question").type == QuestionTypes.administration:
            attrs["value"] = int(float(attrs.get("value")))

        return attrs

    class Meta:
        model = Answers
        fields = ["question", "value", "index"]


class SubmitFormSerializer(serializers.Serializer):
    data = SubmitFormDataSerializer()
    answer = SubmitFormDataAnswerSerializer(many=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        data = validated_data.get("data")
        data["form"] = self.context.get("form")
        data["created_by"] = self.context.get("user")
        data["updated_by"] = self.context.get("user")
        obj_data = self.fields.get("data").create(data)
        # Answer value based on Question type
        # - geo = 1 #option
        # - administration = 2 #value
        # - text = 3 #name
        # - number = 4 #value
        # - option = 5 #option
        # - multiple_option = 6 #option
        # - cascade = 7 #option
        # - photo = 8 #name
        # - date = 9 #name
        # - autofield = 10 #name
        # - attachment = 11 #name

        for answer in validated_data.get("answer"):
            name = None
            value = None
            option = None

            if answer.get("question").type in [
                QuestionTypes.geo,
                QuestionTypes.option,
                QuestionTypes.multiple_option,
            ]:
                option = answer.get("value")
            elif answer.get("question").type in [
                QuestionTypes.text,
                QuestionTypes.photo,
                QuestionTypes.date,
                QuestionTypes.autofield,
                QuestionTypes.attachment,
                QuestionTypes.signature,
            ]:
                name = answer.get("value")
            elif answer.get("question").type == QuestionTypes.cascade:
                id = answer.get("value")
                ep = answer.get("question").api.get("endpoint")
                val = None
                if "organisation" in ep:
                    val = Organisation.objects.filter(pk=id).first()
                    val = val.name
                if "entity-data" in ep:
                    val = EntityData.objects.filter(pk=id).first()
                    val = val.name
                if "entity-data" not in ep and "organisation" not in ep:
                    ep = ep.split("?")[0]
                    ep = f"{ep}?id={id}"
                    val = requests.get(ep).json()
                    val = val[0].get("name")
                name = val
            else:
                # for administration,number question type
                value = answer.get("value")

            Answers.objects.create(
                data=obj_data,
                question=answer.get("question"),
                name=name,
                value=value,
                options=option,
                created_by=self.context.get("user"),
            )
        obj_data.save_to_file

        return object


class AnswerHistorySerializer(serializers.Serializer):
    value = serializers.FloatField()
    created = CustomCharField()
    created_by = CustomCharField()


class ListDataAnswerSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    @extend_schema_field(AnswerHistorySerializer(many=True))
    def get_history(self, instance):
        answer_history = AnswerHistory.objects.filter(
            data=instance.data, question=instance.question
        ).all()
        history = []
        for h in answer_history:
            history.append(get_answer_history(h))
        return history if history else None

    @extend_schema_field(OpenApiTypes.ANY)
    def get_value(self, instance: Answers):
        return get_answer_value(instance)

    class Meta:
        model = Answers
        fields = ["history", "question", "value", "index"]


class FormDataSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    @extend_schema_field(ListDataAnswerSerializer(many=True))
    def get_answers(self, instance):
        return ListDataAnswerSerializer(
            instance=instance.data_answer.all(), many=True
        ).data

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
            "submitter",
            "duration",
            "answers",
        ]


class ListFormDataRequestSerializer(serializers.Serializer):
    administration = CustomPrimaryKeyRelatedField(
        queryset=Administration.objects.none(), required=False
    )
    questions = CustomListField(
        child=CustomPrimaryKeyRelatedField(queryset=Questions.objects.none()),
        required=False,
    )
    parent = serializers.CharField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get(
            "administration"
        ).queryset = Administration.objects.all()
        self.fields.get("questions").child.queryset = Questions.objects.all()


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
        pending_data = instance.children.filter(
            is_pending=True,
        ).first()
        if pending_data:
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


class ListOptionsChartCriteriaSerializer(serializers.Serializer):
    question = CustomPrimaryKeyRelatedField(queryset=Questions.objects.none())
    option = CustomListField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get("question").queryset = Questions.objects.all()


class ListPendingDataAnswerSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    last_value = serializers.SerializerMethodField()

    @extend_schema_field(AnswerHistorySerializer(many=True))
    def get_history(self, instance):
        answer_history = AnswerHistory.objects.filter(
            data=instance.data, question=instance.question
        ).all()
        history = []
        for h in answer_history:
            history.append(get_answer_history(h))
        return history if history else None

    @extend_schema_field(OpenApiTypes.ANY)
    def get_value(self, instance: Answers):
        return get_answer_value(instance)

    @extend_schema_field(OpenApiTypes.ANY)
    def get_last_value(self, instance: Answers):
        if self.context["last_data"]:
            parent_question = None
            if instance.question.form.parent:
                # If the question is from a parent form,
                # get the parent question from the parent form
                qg = instance.question.form.parent \
                    .form_question_group.filter(
                        name=instance.question.question_group.name
                    ).first()
                if qg:
                    parent_question = qg.question_group_question.filter(
                        name=instance.question.name
                    ).first()
            answer = (
                self.context["last_data"]
                .data_answer.filter(
                    Q(
                        question=instance.question,
                        index=instance.index,
                    ) |
                    Q(
                        question=parent_question,
                        index=instance.index,
                    )
                )
                .first()
            )
            if answer:
                return get_answer_value(answer=answer)
        return None

    class Meta:
        model = Answers
        fields = ["history", "question", "value", "last_value", "index"]


class ParentFormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormData
        fields = [
            "id",
            "name",
            "form",
            "is_pending",
        ]


class ListPendingFormDataSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    administration = serializers.ReadOnlyField(source="administration.name")
    answer_history = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

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

    @extend_schema_field(ParentFormDataSerializer)
    def get_parent(self, instance: FormData):
        if instance.parent:
            return ParentFormDataSerializer(instance=instance.parent).data
        return None

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
            "parent",
        ]


class SubmitPendingFormSerializer(serializers.Serializer):
    data = SubmitFormDataSerializer()
    answer = SubmitFormDataAnswerSerializer(many=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, validated_data):
        data = validated_data.get("data")
        data["form"] = self.context.get("form")
        data["created_by"] = self.context.get("user")

        # check user role and form type
        user = self.context.get("user")
        is_super_admin = user.is_superuser

        direct_to_data = is_super_admin

        obj_data = self.fields.get("data").create(data)
        # If the form is a child form, it should have a parent
        if data.get("uuid") and obj_data.form.parent:
            obj_data.uuid = data["uuid"]
            # find parent data by uuid and parent form
            parent_data = FormData.objects.filter(
                uuid=data["uuid"],
                form__parent__isnull=True,
            ).first()
            if parent_data:
                # if parent data exists, link the child data
                obj_data.parent = parent_data
                obj_data.geo = parent_data.geo
                obj_data.administration = parent_data.administration
            obj_data.save()

        if not direct_to_data and obj_data.has_approval:
            # If the form has approval
            obj_data.is_pending = True
            obj_data.save()

        answers = []

        for answer in validated_data.get("answer"):
            question = answer.get("question")
            name = None
            value = None
            option = None

            if question.type in [
                QuestionTypes.geo,
                QuestionTypes.option,
                QuestionTypes.multiple_option,
            ]:
                option = answer.get("value")
            elif question.type in [
                QuestionTypes.text,
                QuestionTypes.photo,
                QuestionTypes.date,
                QuestionTypes.autofield,
                QuestionTypes.attachment,
                QuestionTypes.signature,
            ]:
                name = answer.get("value")
            elif question.type == QuestionTypes.cascade:
                id = answer.get("value")
                val = None
                if question.api:
                    ep = question.api.get("endpoint")
                    if "organisation" in ep:
                        name = Organisation.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" in ep:
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" not in ep and "organisation" not in ep:
                        ep = ep.split("?")[0]
                        ep = f"{ep}?id={id}"
                        val = requests.get(ep).json()
                        val = val[0].get("name")

                if question.extra:
                    cs_type = question.extra.get("type")
                    if cs_type == "entity":
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                name = val
            else:
                # for administration,number question type
                value = answer.get("value")

            answers.append(Answers(
                data=obj_data,
                question=question,
                name=name,
                value=value,
                options=option,
                created_by=self.context.get("user"),
                index=answer.get("index", 0)
            ))

        Answers.objects.bulk_create(answers)

        if direct_to_data and not obj_data.parent and not obj_data.is_pending:
            # Only save to file if the data is not pending
            # and does not have a parent
            obj_data.save_to_file

        return obj_data


class SubmitDraftFormSerializer(SubmitPendingFormSerializer):
    """
    Serializer for creating draft form data.
    Extends SubmitPendingFormSerializer but sets is_draft=True
    and doesn't save to file.
    """

    def create(self, validated_data):
        data = validated_data.get("data")
        data["form"] = self.context.get("form")
        data["created_by"] = self.context.get("user")

        # Create the form data object
        obj_data = self.fields.get("data").create(data)

        # If the form is a child form, it should have a parent
        if data.get("uuid") and obj_data.form.parent:
            obj_data.uuid = data["uuid"]
            # find parent data by uuid and parent form
            parent_data = FormData.objects.filter(
                uuid=data["uuid"],
                form__parent__isnull=True,
            ).first()
            if parent_data:
                # if parent data exists, link the child data
                obj_data.parent = parent_data
                obj_data.geo = parent_data.geo
                obj_data.administration = parent_data.administration
            obj_data.save()
        # Mark as draft
        obj_data.mark_as_draft()

        answers = []

        for answer in validated_data.get("answer"):
            question = answer.get("question")
            name = None
            value = None
            option = None

            if question.type in [
                QuestionTypes.geo,
                QuestionTypes.option,
                QuestionTypes.multiple_option,
            ]:
                option = answer.get("value")
            elif question.type in [
                QuestionTypes.text,
                QuestionTypes.photo,
                QuestionTypes.date,
                QuestionTypes.autofield,
                QuestionTypes.attachment,
                QuestionTypes.signature,
            ]:
                name = answer.get("value")
            elif question.type == QuestionTypes.cascade:
                id = answer.get("value")
                val = None
                if question.api:
                    ep = question.api.get("endpoint")
                    if "organisation" in ep:
                        name = Organisation.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" in ep:
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" not in ep and "organisation" not in ep:
                        ep = ep.split("?")[0]
                        ep = f"{ep}?id={id}"
                        val = requests.get(ep).json()
                        val = val[0].get("name")

                if question.extra:
                    cs_type = question.extra.get("type")
                    if cs_type == "entity":
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                name = val
            else:
                value = answer.get("value")

            answers.append(Answers(
                data=obj_data,
                question=question,
                name=name,
                value=value,
                options=option,
                created_by=self.context.get("user"),
                index=answer.get("index", 0)
            ))

        Answers.objects.bulk_create(answers)

        # Don't save to file for drafts
        return obj_data


class SubmitUpdateDraftFormSerializer(SubmitDraftFormSerializer):
    """
    Serializer for updating existing draft form data.
    """

    def update(self, instance, validated_data):
        data = validated_data.get("data")

        # Update the FormData instance
        instance.name = data.get("name", instance.name)
        admin_id = data.get("administration", instance.administration_id)
        instance.administration_id = admin_id
        instance.geo = data.get("geo", instance.geo)
        instance.updated = timezone.now()
        instance.updated_by = self.context.get("user")
        instance.save()

        # Clear existing answers and create new ones
        instance.data_answer.all().delete()

        answers = []
        for answer in validated_data.get("answer"):
            question = answer.get("question")
            name = None
            value = None
            option = None

            if question.type in [
                QuestionTypes.geo,
                QuestionTypes.option,
                QuestionTypes.multiple_option,
            ]:
                option = answer.get("value")
            elif question.type in [
                QuestionTypes.text,
                QuestionTypes.photo,
                QuestionTypes.date,
                QuestionTypes.autofield,
                QuestionTypes.attachment,
                QuestionTypes.signature,
            ]:
                name = answer.get("value")
            elif question.type == QuestionTypes.cascade:
                id = answer.get("value")
                val = None
                if question.api:
                    ep = question.api.get("endpoint")
                    if "organisation" in ep:
                        name = Organisation.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" in ep:
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                    if "entity-data" not in ep and "organisation" not in ep:
                        ep = ep.split("?")[0]
                        ep = f"{ep}?id={id}"
                        val = requests.get(ep).json()
                        val = val[0].get("name")

                if question.extra:
                    cs_type = question.extra.get("type")
                    if cs_type == "entity":
                        name = EntityData.objects.filter(pk=id).values_list(
                            'name', flat=True).first()
                        val = name
                name = val
            else:
                # for administration,number question type
                value = answer.get("value")

            answers.append(Answers(
                data=instance,
                question=question,
                name=name,
                value=value,
                options=option,
                created_by=self.context.get("user"),
                index=answer.get("index", 0)
            ))

        Answers.objects.bulk_create(answers)
        return instance
