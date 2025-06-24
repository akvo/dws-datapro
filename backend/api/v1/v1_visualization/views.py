from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from api.v1.v1_data.models import FormData, Answers
from api.v1.v1_visualization.serializers import FormDataStatSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    description="Get the statistic of a particular question on monitoring data",
    tags=["Visualization"],
    responses=FormDataStatSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name="parent_id",
            required=True,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="The parent ID to filter FormData",
        ),
        OpenApiParameter(
            name="question_id",
            required=True,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="The question ID to extract the value from",
        ),
        OpenApiParameter(
            name="question_date",
            required=False,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="The name of the question to extract the date from (optional)",
        ),
    ],
)
@api_view(["GET"])
def formdata_stats(request, version):
    parent_id = request.query_params.get("parent_id")
    question_id = request.query_params.get("question_id")
    question_date_key = request.query_params.get("question_date")

    if not parent_id or not question_id:
        return Response(
            {"detail": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        formdata_qs = FormData.objects.filter(parent_id=parent_id)
        stats = []

        for formdata in formdata_qs:
            answer = Answers.objects.filter(
                data=formdata, question_id=question_id
            ).first()
            if not answer:
                continue

            # Default date
            date = formdata.created

            # Optional override from another question
            if question_date_key:
                date_answer = Answers.objects.filter(
                    data=formdata, question__name=question_date_key
                ).first()
                if date_answer and date_answer.name:
                    parsed_date = parse_date(date_answer.name)
                    if parsed_date:
                        date = parsed_date

            stats.append(
                {
                    "date": date.date(),
                    "value": answer.name or answer.value or answer.options,
                }
            )

        serializer = FormDataStatSerializer(stats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
