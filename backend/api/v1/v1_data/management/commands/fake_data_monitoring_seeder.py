# import pandas as pd
from django.core.management import BaseCommand
from django.core.management import call_command
from faker import Faker
from api.v1.v1_data.models import FormData
from api.v1.v1_approval.models import (
    DataBatch,
    DataApproval,
    DataApprovalStatus,
)
from api.v1.v1_data.functions import add_fake_answers

fake = Faker()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-r", "--repeat", nargs="?", const=20, default=20, type=int
        )
        parser.add_argument(
            "-t", "--test", nargs="?", const=False, default=False, type=bool
        )
        parser.add_argument(
            "-a",
            "--approved",
            nargs="?",
            const=False,
            default=True,
            type=bool,
        )

    def handle(self, *args, **options):
        test = options.get("test")
        repeat = options.get("repeat")
        approved = options.get("approved")

        if test:
            # Call fake_data_seeder with test=True
            call_command(
                "fake_data_seeder",
                test=True,
                repeat=repeat,
            )

        data = FormData.objects.filter(
            is_pending=False,
            form__parent__isnull=True,
        ).all()[:repeat]

        for d in data:
            items = []
            for f in d.form.children():
                # random date
                created = fake.date_time_this_decade()
                # format Y-m-d H:M:S
                created = created.strftime("%Y-%m-%d %H:%M:%S")
                monitoring_data = FormData.objects.create(
                    name=f"{created} - {d.name}",
                    form=f,
                    created=created,
                    created_by=d.created_by,
                    administration=d.administration,
                    geo=d.geo,
                    uuid=d.uuid,
                )
                add_fake_answers(monitoring_data)
                items.append(monitoring_data)

            if (
                d.has_approval and
                not approved
            ):
                for i in items:
                    i.is_pending = True
                    i.save()

            if d.has_approval and approved:
                # Create Batch for approved data
                batch = DataBatch.objects.create(
                    name=f"Batch for {d.name}",
                    form=d.form,
                    created_by=d.created_by,
                    approved=True,
                )
                # Add items to DataBatchList
                batch.data_batch_list.set(items)

                # Add DataApproval
                for approver in batch.approvers:
                    DataApproval.objects.create(
                        batch=batch,
                        administration=approver["administration"],
                        role=approver["role"],
                        user=approver["user"],
                        status=DataApprovalStatus.approved
                    )
                    batch.batch_batch_comments.create(
                        user=approver["user"],
                        comment=f"Data approved by {approver['user'].email}",
                    )
