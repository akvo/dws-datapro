from django.core.management import BaseCommand
from api.v1.v1_users.models import SystemUser
from api.v1.v1_forms.models import Forms


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("email", nargs="+", type=str)

    def handle(self, *args, **options):
        email = options.get("email")
        user = SystemUser.objects.filter(email=email[0]).first()
        if not user:
            self.stdout.write("User doesn't exist")
            exit()
        forms = Forms.objects.filter(parent__isnull=True).all()
        for form in forms:
            user.user_form.create(
                form=form
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully assigned {len(forms)} forms "
                f"to user {user.email}."
            )
        )
