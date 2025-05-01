from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from utils.custom_serializer_fields import CustomFileField


class UploadImagesSerializer(serializers.Serializer):
    file = CustomFileField(
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])]
    )


class AttachmentsSerializer(serializers.Serializer):
    file = CustomFileField(
        allow_empty_file=False,
        required=True,
    )

    def validate_file(self, value):
        """
        Validate the file type against allowed file types.
        This method checks if the file extension is in the list of allowed
        file types provided in the context.
        If the file type is not allowed, it raises a ValidationError.
        """
        allowed_file_types = self.context.get("allowed_file_types", [])
        validator = FileExtensionValidator(allowed_file_types)
        try:
            validator(value)
            return value
        except serializers.ValidationError as e:
            raise serializers.ValidationError(
                f"File type not allowed. {str(e)}"
            )

    class Meta:
        fields = ["file"]
