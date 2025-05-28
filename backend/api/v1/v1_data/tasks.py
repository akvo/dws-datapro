from api.v1.v1_data.models import (
    FormData,
    Answers,
    PendingAnswers,
)


def seed_approved_data(data):
    parent_data = FormData.objects.filter(
        form=data.form,
        uuid=data.uuid,
        parent__isnull=True,
    ).first()
    form_data = FormData.objects.create(
        parent=parent_data,
        name=data.name,
        uuid=data.uuid,
        form=data.form,
        administration=data.administration,
        geo=data.geo,
        created_by=data.created_by,
        created=data.created,
    )
    data.data = form_data
    data.approved = True
    data.save()

    answer: PendingAnswers
    for answer in data.pending_data_answer.all():
        Answers.objects.create(
            data=form_data,
            question=answer.question,
            name=answer.name,
            value=answer.value,
            options=answer.options,
            created_by=answer.created_by,
        )

    form_data.save_to_file
