class DataApprovalStatus:
    pending = 1
    approved = 2
    rejected = 3

    FieldStr = {
        pending: "Pending",
        approved: "Approved",
        rejected: "Rejected",
    }


# Allowed file extensions for batch attachments
allowed_batch_attach = [
    "xls",
    "xlsx",
    "pdf",
    "doc",
    "docx",
    "csv",
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    "odt",
    "ods",
]
