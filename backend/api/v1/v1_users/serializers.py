from django.core import signing
from django.core.signing import BadSignature
from django.utils import timezone
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# from api.v1.v1_approval.constants import DataApprovalStatus
from api.v1.v1_forms.models import (
    UserForms,
    Forms,
)
from api.v1.v1_profile.constants import OrganisationTypes
from api.v1.v1_profile.models import (
    Administration,
    Levels,
    Role,
    UserRole,
)
from api.v1.v1_users.models import SystemUser, \
        Organisation, OrganisationAttribute
from api.v1.v1_mobile.models import MobileAssignment
from api.v1.v1_approval.models import DataBatch
from utils.custom_serializer_fields import (
    CustomEmailField,
    CustomCharField,
    CustomPrimaryKeyRelatedField,
    CustomBooleanField,
    CustomMultipleChoiceField,
)
from utils.custom_helper import CustomPasscode
from utils.custom_generator import update_sqlite


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['id', 'name']


class OrganisationAttributeSerializer(serializers.ModelSerializer):
    type_id = serializers.ReadOnlyField(source='type')
    name = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, instance: OrganisationAttribute):
        return OrganisationTypes.FieldStr.get(instance.type)

    class Meta:
        model = OrganisationAttribute
        fields = ['type_id', 'name']


class OrganisationAttributeChildrenSerializer(serializers.ModelSerializer):
    type_id = serializers.ReadOnlyField(source='type')
    name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, instance: OrganisationAttribute):
        return OrganisationTypes.FieldStr.get(instance.type)

    @extend_schema_field(OrganisationSerializer(many=True))
    def get_children(self, instance: OrganisationAttribute):
        orgs = Organisation.objects.filter(
            organisation_organisation_attribute__type=instance.type
        ).all()
        return OrganisationSerializer(instance=orgs, many=True).data

    class Meta:
        model = OrganisationAttribute
        fields = ['type_id', 'name', 'children']


class OrganisationListSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    users = serializers.IntegerField(source='user_count')

    @extend_schema_field(OrganisationAttributeSerializer(many=True))
    def get_attributes(self, instance: Organisation):
        # Use the prefetched data instead of querying the database again
        attr = instance.organisation_organisation_attribute.all()
        return OrganisationAttributeSerializer(instance=attr, many=True).data

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'attributes', 'users']


class AddEditOrganisationSerializer(serializers.ModelSerializer):
    attributes = CustomMultipleChoiceField(choices=list(
        OrganisationTypes.FieldStr.keys()),
                                           required=True)

    def create(self, validated_data):
        attributes = validated_data.pop('attributes')
        instance = super(AddEditOrganisationSerializer,
                         self).create(validated_data)
        for attr in attributes:
            OrganisationAttribute.objects.create(organisation=instance,
                                                 type=attr)
        update_sqlite(
            model=Organisation,
            data={
                'id': instance.id,
                'name': instance.name,
            }
        )
        return instance

    def update(self, instance, validated_data):
        attributes = validated_data.pop('attributes')
        instance: Organisation = super(AddEditOrganisationSerializer,
                                       self).update(instance, validated_data)
        instance.save()
        current_attributes = OrganisationAttribute.objects.filter(
            organisation=instance).all()
        for attr in current_attributes:
            if attr.type not in attributes:
                attr.delete()
        for attr in attributes:
            attr, created = OrganisationAttribute.objects.get_or_create(
                organisation=instance, type=attr)
            attr.save()
        update_sqlite(
            model=Organisation,
            data={'name': instance.name},
            id=instance.id
        )
        return instance

    class Meta:
        model = Organisation
        fields = ['name', 'attributes']


class LoginSerializer(serializers.Serializer):
    email = CustomEmailField()
    password = CustomCharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = CustomEmailField()

    def validate_email(self, email):
        try:
            user = SystemUser.objects.get(email=email, deleted_at=None)
        except SystemUser.DoesNotExist:
            raise ValidationError('Invalid email, user not found')
        return user


class VerifyInviteSerializer(serializers.Serializer):
    invite = CustomCharField()

    def validate_invite(self, invite):
        try:
            pk = signing.loads(invite)
            user = SystemUser.objects.get(pk=pk)
        except BadSignature:
            raise ValidationError('Invalid invite code')
        except SystemUser.DoesNotExist:
            raise ValidationError('Invalid invite code')
        return user


class SetUserPasswordSerializer(serializers.Serializer):
    password = CustomCharField()
    confirm_password = CustomCharField()
    invite = CustomCharField()

    def validate_invite(self, invite):
        try:
            pk = signing.loads(invite)
            user = SystemUser.objects.get(pk=pk, deleted_at=None)
        except BadSignature:
            raise ValidationError('Invalid invite code')
        except SystemUser.DoesNotExist:
            raise ValidationError('Invalid invite code')
        return user

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise ValidationError({
                'confirm_password':
                'Confirm password and password'
                ' are not same'
            })
        return attrs


class ListAdministrationChildrenSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_full_name(self, instance: Administration):
        return instance.full_path_name

    class Meta:
        model = Administration
        fields = ['id', 'parent', 'path', 'level', 'name', 'full_name']


class ListAdministrationSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    level_name = serializers.ReadOnlyField(source='level.name')
    level = serializers.ReadOnlyField(source='level.level')
    children_level_name = serializers.SerializerMethodField()

    @extend_schema_field(ListAdministrationChildrenSerializer(many=True))
    def get_children(self, instance: Administration):
        max_level = self.context.get('max_level')
        filter_children = self.context.get('filter_children')
        if max_level:
            if int(max_level) <= instance.level.level:
                return []
        filter = self.context.get('filter')
        if filter:
            filtered_administration = Administration.objects.filter(
                id=filter).all().order_by('name')
            return ListAdministrationChildrenSerializer(
                filtered_administration, many=True).data
        children = instance.parent_administration.all().order_by('name')
        if len(filter_children):
            children = instance.parent_administration.filter(
                pk__in=filter_children
            ).all().order_by('name')
        return ListAdministrationChildrenSerializer(
            instance=children,
            many=True
        ).data

    @extend_schema_field(OpenApiTypes.STR)
    def get_children_level_name(self, instance: Administration):
        child: Administration = instance.parent_administration.first()
        if child:
            return child.level.name
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_full_name(self, instance: Administration):
        return instance.full_path_name

    class Meta:
        model = Administration
        fields = [
            'id', 'full_name', 'path', 'parent', 'name',
            'level_name', 'level', 'children',
            'children_level_name'
        ]


class AddRolesSerializer(serializers.Serializer):
    role = CustomPrimaryKeyRelatedField(
        queryset=Role.objects.none(),
        required=True,
        help_text='Role to assign to user'
    )
    administration = CustomPrimaryKeyRelatedField(
        queryset=Administration.objects.none(),
        required=True,
        help_text='Administration to assign role to user'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get('role').queryset = Role.objects.all()
        admin_field = self.fields.get('administration')
        admin_field.queryset = Administration.objects.all()

    class Meta:
        fields = ['role', 'administration']


class AddEditUserSerializer(serializers.ModelSerializer):
    organisation = CustomPrimaryKeyRelatedField(
        queryset=Organisation.objects.none(), required=False)
    trained = CustomBooleanField(default=False)
    roles = AddRolesSerializer(many=True, required=False)
    forms = CustomPrimaryKeyRelatedField(
        queryset=Forms.objects.filter(parent__isnull=True).all(),
        many=True,
        required=False,
    )
    inform_user = CustomBooleanField(default=True)
    is_superuser = CustomBooleanField(
        default=False,
        required=False,
        help_text='Set user as superuser. Superuser can access all data.'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get('organisation').queryset = Organisation.objects.all()

    def validate(self, attrs):
        if self.instance:
            if (
                not self.context.get('user').is_superuser
                and self.instance == self.context.get('user')
            ):
                raise ValidationError(
                    'You do not have permission to edit this user'
                )
        return attrs

    def create(self, validated_data):
        try:
            user_deleted = SystemUser.objects_deleted.get(
                email=validated_data['email']
            )
            if user_deleted:
                user_deleted.restore()
                self.update(
                    instance=user_deleted,
                    validated_data=validated_data
                )
                return user_deleted
        except SystemUser.DoesNotExist:
            # delete inform_user payload
            validated_data.pop('inform_user', None)
            roles_data = validated_data.pop('roles', [])
            forms = validated_data.pop('forms', [])
            user = super(AddEditUserSerializer, self).create(validated_data)
            # Assign roles to user
            if roles_data:
                for role_data in roles_data:
                    UserRole.objects.create(
                        user=user,
                        administration=role_data['administration'],
                        role=role_data['role']
                    )
            # add new user forms
            for form in forms:
                UserForms.objects.create(user=user, form=form)
            # if forms is empty and is_superuser is True
            # then assign all parent forms to user
            if not forms and user.is_superuser:
                parent_forms = Forms.objects.filter(
                    parent__isnull=True
                ).all()
                for form in parent_forms:
                    UserForms.objects.create(user=user, form=form)
            return user

    def update(self, instance, validated_data):
        # delete inform_user payload
        validated_data.pop('inform_user', None)
        # pop roles request data
        roles_data = validated_data.pop('roles', [])
        # pop forms request data
        forms = validated_data.pop('forms', [])
        instance: SystemUser = super(
            AddEditUserSerializer,
            self
        ).update(instance, validated_data)
        instance.updated = timezone.now()
        instance.save()
        # Delete old user forms
        user_forms = UserForms.objects.filter(user=instance).all()
        if user_forms:
            user_forms.delete()
        # add new user forms
        if forms:
            for form in forms:
                UserForms.objects.create(user=instance, form=form)
        # Handle multiple role assignments
        if roles_data:
            # Get existing roles
            existing_roles = UserRole.objects.filter(user=instance).all()
            # Create a set of unique identifiers for existing roles
            existing_role_identifiers = {
                (str(role.role.id), str(role.administration.id)): role
                for role in existing_roles
            }

            # Create a set of unique identifiers for new roles
            new_role_identifiers = {}
            for role_data in roles_data:
                role_id = str(role_data['role'].id)
                admin_id = str(role_data['administration'].id)
                new_role_identifiers[(role_id, admin_id)] = role_data
            # Delete roles that are not in the new set
            for key, role in list(existing_role_identifiers.items()):
                if key not in new_role_identifiers:
                    role.delete()
            # Create or update roles
            for key, role_data in new_role_identifiers.items():
                if key in existing_role_identifiers:
                    # Update existing role
                    role = existing_role_identifiers[key]
                    role.role = role_data['role']
                    role.administration = role_data['administration']
                    role.save()
                else:
                    # Create new role
                    UserRole.objects.create(
                        user=instance,
                        administration=role_data['administration'],
                        role=role_data['role']
                    )
        else:
            # If no roles provided, delete all roles
            UserRole.objects.filter(user=instance).delete()
        return instance

    def to_internal_value(self, data):
        roles_data = data.pop('roles', None)
        internal_value = super().to_internal_value(data)

        if roles_data:
            # Validate each role data
            serializer = AddRolesSerializer(data=roles_data, many=True)
            if not serializer.is_valid():
                errors = {}
                # Process role validation errors
                if any('role' in item for item in serializer.errors):
                    role_errors = []
                    for i, error_item in enumerate(serializer.errors):
                        if 'role' in error_item:
                            for err in error_item['role']:
                                if 'does not exist' in str(err):
                                    try:
                                        invalid_id = str(roles_data[i]['role'])
                                        role_errors.append(
                                            f"Invalid role ID: {invalid_id}"
                                        )
                                    except (IndexError, KeyError):
                                        role_errors.append("Invalid role ID")
                                else:
                                    role_errors.append(str(err))
                    if role_errors:
                        errors['role'] = role_errors

                # Process administration validation errors
                if any('administration' in item for item in serializer.errors):
                    admin_errors = []
                    for i, error_item in enumerate(serializer.errors):
                        if 'administration' in error_item:
                            for err in error_item['administration']:
                                if 'does not exist' in str(err):
                                    try:
                                        invalid_id = str(
                                            roles_data[i]['administration']
                                        )
                                        admin_errors.append(
                                            f"Invalid administration ID: "
                                            f"{invalid_id}"
                                        )
                                    except (IndexError, KeyError):
                                        admin_errors.append(
                                            "Invalid administration ID"
                                        )
                                else:
                                    admin_errors.append(str(err))
                    if admin_errors:
                        errors['administration'] = admin_errors
                # Raise custom ValidationError with better error messages
                if errors:
                    raise ValidationError(errors)
                # Otherwise, re-raise the original errors
                raise ValidationError(serializer.errors)
            internal_value['roles'] = serializer.validated_data

        return internal_value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Get user roles
        user_roles = UserRole.objects.filter(user=instance).all()

        # Convert roles to representation
        roles_data = []
        for role in user_roles:
            roles_data.append({
                'role': role.role.id,
                'administration': role.administration.id
            })

        representation['roles'] = roles_data
        return representation

    class Meta:
        model = SystemUser
        fields = [
            'first_name', 'last_name', 'email',
            'organisation', 'trained', 'roles', 'phone_number',
            'forms', 'inform_user', 'is_superuser'
        ]


class UserAdministrationSerializer(serializers.ModelSerializer):
    level = serializers.ReadOnlyField(source='level.level')
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance: Administration):
        return instance.full_name

    class Meta:
        model = Administration
        fields = ['id', 'name', 'level', 'full_name']


class UserFormSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='form.id')
    name = serializers.ReadOnlyField(source='form.name')

    class Meta:
        model = UserForms
        fields = ["id", "name"]


class ListUserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    trained = CustomBooleanField()
    invite = serializers.SerializerMethodField()
    forms = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()

    @extend_schema_field(AddRolesSerializer(many=True))
    def get_roles(self, instance: SystemUser):
        user_roles = UserRole.objects.filter(user=instance).all()
        roles_data = []
        for role in user_roles:
            roles_data.append({
                'role': role.role.id,
                'administration': role.administration.id
            })
        return roles_data

    @extend_schema_field(OrganisationSerializer)
    def get_organisation(self, instance: SystemUser):
        return OrganisationSerializer(instance=instance.organisation).data

    @extend_schema_field(OpenApiTypes.STR)
    def get_invite(self, instance: SystemUser):
        return signing.dumps(instance.id)

    @extend_schema_field(UserFormSerializer(many=True))
    def get_forms(self, instance: SystemUser):
        return UserFormSerializer(instance=instance.user_form.all(),
                                  many=True).data

    @extend_schema_field(OpenApiTypes.INT)
    def get_last_login(self, instance):
        if instance.last_login:
            return instance.last_login.timestamp()
        return None

    class Meta:
        model = SystemUser
        fields = [
            'id', 'first_name', 'last_name', 'email', 'roles',
            'organisation', 'trained', 'phone_number',
            'invite', 'forms', 'last_login'
        ]


class ListUserRequestSerializer(serializers.Serializer):
    trained = CustomCharField(required=False, default=None)
    organisation = CustomPrimaryKeyRelatedField(
        queryset=Organisation.objects.none(), required=False)
    administration = CustomPrimaryKeyRelatedField(
        queryset=Administration.objects.none(), required=False)
    pending = CustomBooleanField(default=False)
    descendants = CustomBooleanField(default=True)
    search = CustomCharField(required=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields.get(
            'administration').queryset = Administration.objects.all()
        self.fields.get('organisation').queryset = Organisation.objects.all()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    administration = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    trained = CustomBooleanField(default=False)
    forms = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    passcode = serializers.SerializerMethodField()

    @extend_schema_field(UserAdministrationSerializer)
    def get_administration(self, instance: SystemUser):
        if instance.is_superuser:
            adm = Administration.objects.filter(
                parent__isnull=True,
                level__level=0
            ).first()
            return UserAdministrationSerializer(instance=adm).data
        # Order UserRole by administration level and get the first one
        user_role = UserRole.objects.filter(user=instance) \
            .order_by('administration__level__level').first()
        if user_role:
            return UserAdministrationSerializer(
                instance=user_role.administration
            ).data
        return None

    @extend_schema_field(AddRolesSerializer(many=True))
    def get_roles(self, instance: SystemUser):
        if instance.is_superuser:
            adm = Administration.objects.filter(
                parent__isnull=True,
                level__level=0
            ).first()
            return [
                {
                    "role": "Super Admin",
                    "administration": UserAdministrationSerializer(
                        instance=adm
                    ).data,
                    "is_approver": True,
                    "is_submitter": True,
                    "is_editor": True,
                }
            ]
        user_roles = UserRole.objects.filter(user=instance).all()
        roles_data = []
        for role in user_roles:
            roles_data.append({
                'role': role.role.name,
                'administration': UserAdministrationSerializer(
                    instance=role.administration
                ).data,
                'is_approver': True if role.is_approver else False,
                'is_submitter': True if role.is_submitter else False,
                'is_editor': True if role.is_editor else False,
            })
        return roles_data

    @extend_schema_field(OrganisationSerializer)
    def get_organisation(self, instance: SystemUser):
        return OrganisationSerializer(instance=instance.organisation).data

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, instance):
        return instance.get_full_name()

    @extend_schema_field(UserFormSerializer(many=True))
    def get_forms(self, instance: SystemUser):
        return UserFormSerializer(instance=instance.user_form.all(),
                                  many=True).data

    @extend_schema_field(OpenApiTypes.INT)
    def get_last_login(self, instance):
        if instance.last_login:
            return instance.last_login.timestamp()
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_passcode(self, instance: SystemUser):
        mobile_assignment = MobileAssignment \
            .objects.filter(user=instance).first()
        if mobile_assignment:
            passcode = CustomPasscode().decode(mobile_assignment.passcode)
            return passcode
        return None

    class Meta:
        model = SystemUser
        fields = [
            'email', 'name', 'roles', 'trained',
            'phone_number', 'forms', 'organisation',
            'last_login', 'passcode', 'is_superuser',
            'administration',
        ]


class ListLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Levels
        fields = ['id', 'name', 'level']


class UserDetailSerializer(serializers.ModelSerializer):
    administration = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    trained = CustomBooleanField(default=False)
    forms = serializers.SerializerMethodField()
    pending_approval = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    pending_batch = serializers.SerializerMethodField()

    @extend_schema_field(UserAdministrationSerializer)
    def get_administration(self, instance: SystemUser):
        if instance.is_superuser:
            adm = Administration.objects.filter(
                parent__isnull=True,
                level__level=0
            ).first()
            return UserAdministrationSerializer(instance=adm).data
        # Order UserRole by administration level and get the first one
        user_role = UserRole.objects.filter(user=instance) \
            .order_by('administration__level__level').first()
        if user_role:
            return UserAdministrationSerializer(
                instance=user_role.administration
            ).data
        return None

    @extend_schema_field(AddRolesSerializer(many=True))
    def get_roles(self, instance: SystemUser):
        roles_data = []
        for role in instance.user_user_role.all():
            roles_data.append({
                'role': role.role.id,
                'administration': role.administration.id,
            })
        return roles_data

    @extend_schema_field(OrganisationSerializer)
    def get_organisation(self, instance: SystemUser):
        return OrganisationSerializer(instance=instance.organisation).data

    @extend_schema_field(UserFormSerializer(many=True))
    def get_forms(self, instance: SystemUser):
        return UserFormSerializer(instance=instance.user_form.all(),
                                  many=True).data

    @extend_schema_field(OpenApiTypes.INT)
    def get_pending_approval(self, instance: SystemUser):
        batch_q = Q(approved=False)
        for ur in instance.user_user_role.all():
            adm = ur.administration
            path = adm.path \
                if hasattr(adm, 'path') and adm.path else f"{adm.id}."
            batch_q |= Q(
                administration__path__startswith=path,
                approved=False,
            )
        total_batches = DataBatch.objects.filter(batch_q).count()
        return total_batches

    @extend_schema_field(OpenApiTypes.INT)
    def get_data(self, instance: SystemUser):
        return instance.form_data_created.all().count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_pending_batch(self, instance: SystemUser):
        return instance.user_data_batch.filter(
            approved=False).all().count()

    class Meta:
        model = SystemUser
        fields = [
            'first_name', 'last_name', 'email', 'roles',
            'organisation', 'trained', 'phone_number',
            'forms', 'pending_approval', 'data',
            'pending_batch', 'is_superuser', 'administration',
        ]


class RoleOptionSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='name')
    value = serializers.IntegerField(source='id')

    class Meta:
        model = Role
        fields = ["label", "value", "administration_level"]
