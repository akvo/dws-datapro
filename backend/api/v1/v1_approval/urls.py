from django.urls import re_path

from api.v1.v1_approval.views import (
    approve_pending_data,
    list_pending_batch,
    list_data_batch,
    BatchView,
    BatchSummaryView,
    BatchCommentView,
)

urlpatterns = [
    re_path(r"^(?P<version>(v1))/form-pending-batch", list_pending_batch),
    re_path(
        r"^(?P<version>(v1))/form-pending-data-batch/(?P<batch_id>[0-9]+)",
        list_data_batch,
    ),
    re_path(r"^(?P<version>(v1))/pending-data/approve", approve_pending_data),
    re_path(
        r"^(?P<version>(v1))/batch/comment/(?P<batch_id>[0-9]+)",
        BatchCommentView.as_view(),
    ),
    re_path(
        r"^(?P<version>(v1))/batch/summary/(?P<batch_id>[0-9]+)",
        BatchSummaryView.as_view(),
    ),
    re_path(r"^(?P<version>(v1))/batch", BatchView.as_view()),
]
