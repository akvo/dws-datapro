from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from api.v1.v1_profile.constants import DataAccessTypes
from api.v1.v1_users.models import SystemUser


class Levels(models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "levels"


class Administration(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        # NOTE: should be named 'children'
        related_name="parent_administration",
        default=None,
        null=True,
    )
    code = models.CharField(max_length=255, null=True, default=None)
    level = models.ForeignKey(
        to=Levels, on_delete=models.CASCADE, related_name="administrator_level"
    )
    name = models.TextField()
    path = models.TextField(null=True, default=None)

    def __str__(self):
        return self.name

    @property
    def ancestors(self):
        if self.path:
            ids = self.path.split(".")[:-1]
            administrations = Administration.objects.filter(
                id__in=ids
            ).order_by("level__level")
            return administrations
        return None

    @property
    def full_name(self):
        if self.path:
            names = " - ".join([a.name for a in self.ancestors])
            return "{} - {}".format(names, self.name)
        return self.name

    @property
    def full_path_name(self):
        if self.path:
            names = "|".join([a.name for a in self.ancestors])
            return "{}|{}".format(names, self.name)
        return self.name

    @property
    def administration_column(self):
        if self.path:
            names = "|".join([a.name for a in self.ancestors])
            return "{}|{}".format(names, self.name)
        return self.name

    class Meta:
        db_table = "administrator"


@receiver(pre_save, sender=Administration)
def set_administration_path(sender, instance: Administration, **_):
    if not instance.parent:
        return
    if instance.path:
        return
    parent = instance.parent
    instance.path = f"{parent.path or ''}{parent.id}."


class AdministrationAttribute(models.Model):
    class Type(models.TextChoices):
        VALUE = "value", "Value"
        OPTION = "option", "Option"
        MULTIPLE_OPTION = "multiple_option", "Multiple option"
        AGGREGATE = "aggregate", "Aggregate"

    name = models.TextField()
    type = models.CharField(
        max_length=25, choices=Type.choices, default=Type.VALUE
    )
    options = ArrayField(
        models.CharField(max_length=255, null=True), default=list, blank=True
    )

    class Meta:
        db_table = "administration_attribute"


class AdministrationAttributeValue(models.Model):
    administration = models.ForeignKey(
        to=Administration, on_delete=models.CASCADE, related_name="attributes"
    )
    attribute = models.ForeignKey(
        to=AdministrationAttribute, on_delete=models.CASCADE
    )
    value = models.JSONField(default=dict)

    class Meta:
        db_table = "administration_attribute_value"


class Entity(models.Model):
    name = models.TextField()

    class Meta:
        db_table = "entities"


class EntityData(models.Model):
    name = models.TextField()
    code = models.CharField(max_length=255, null=True, default=None)
    entity = models.ForeignKey(
        to=Entity, on_delete=models.PROTECT, related_name="entity_data"
    )
    administration = models.ForeignKey(
        to=Administration, on_delete=models.PROTECT, related_name="entity_data"
    )

    class Meta:
        db_table = "entity_data"


# New code for roles and access management


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    administration_level = models.ForeignKey(
        to=Levels,
        on_delete=models.CASCADE,
        related_name="role_administration_level",
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "role"


class RoleAccess(models.Model):
    role = models.ForeignKey(
        to=Role, on_delete=models.CASCADE, related_name="role_role_access"
    )
    data_access = models.IntegerField(
        choices=DataAccessTypes.FieldStr.items(),
        default=DataAccessTypes.read,
    )

    def __str__(self):
        return (
            f"{self.role.name} - {DataAccessTypes.FieldStr[self.data_access]}"
        )

    class Meta:
        unique_together = ("role", "data_access")
        db_table = "role_access"


class UserRole(models.Model):
    user = models.ForeignKey(
        to=SystemUser,
        on_delete=models.CASCADE,
        related_name="user_user_role"
    )
    role = models.ForeignKey(
        to=Role, on_delete=models.CASCADE, related_name="role_user_role"
    )
    administration = models.ForeignKey(
        to=Administration,
        on_delete=models.CASCADE,
        related_name="user_role_administration",
    )

    def is_approver(self):
        return self.role.role_role_access.filter(
            data_access=DataAccessTypes.approve
        ).exists()

    def is_submitter(self):
        return self.role.role_role_access.filter(
            data_access=DataAccessTypes.submit
        ).exists()

    def is_editor(self):
        return self.role.role_role_access.filter(
            data_access=DataAccessTypes.edit
        ).exists()

    def __str__(self):
        return f"{self.user.name} - {self.role.name} ({self.administration})"

    class Meta:
        unique_together = ("user", "role", "administration")
        db_table = "user_role"
