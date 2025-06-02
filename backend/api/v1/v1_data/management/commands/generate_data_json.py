from django.core.management import BaseCommand
from api.v1.v1_data.models import FormData


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--test",
            nargs="?",
            const=1,
            default=False,
            type=int
        )

    def handle(self, *args, **options):
        test = options.get("test")
        data = FormData.objects.filter(
            is_pending=False, form__parent__isnull=True
        ).all()
        for d in data:
            d.save_to_file
        if not test:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully saved {data.count()} "
                    "form data entries to file."
                )
            )
