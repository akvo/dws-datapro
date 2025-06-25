from rest_framework import serializers


class FormDataStatSerializer(serializers.Serializer):
    date = serializers.DateField()
    value = serializers.FloatField()
