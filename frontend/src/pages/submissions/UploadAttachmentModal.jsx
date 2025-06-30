import React, { useState, useMemo } from "react";

import { Modal, Button, Input, Space } from "antd";
import { api, store, uiText } from "../../lib";
import { useNotification } from "../../util/hooks";
import { DocumentUploader } from "../../components";

const UploadAttachmentModal = ({
  onCancel,
  onSuccess,
  isOpen = false,
  editData = {},
  batch = {},
}) => {
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState([]);
  const [comment, setComment] = useState("");

  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);
  const { notify } = useNotification();

  const handleOnCancel = () => {
    setFileList([]);
    setComment("");
    onCancel();
  };

  const handleUpload = () => {
    setLoading(true);

    // Always use FormData for consistency
    const formData = new FormData();
    formData.append("comment", comment);

    const file = fileList[0]; // Assuming single file upload
    if (file) {
      formData.append("file_attachment", file.originFileObj);
    }

    const apiURL = editData?.id
      ? `/batch/attachment/${editData.id}/edit`
      : `/batch/attachments/${batch.id}`;
    api
      .post(apiURL, formData)
      .then(() => {
        notify({
          type: "success",
          message: text.uploadAttachmentsSuccess,
        });
        setFileList([]);
        setComment("");
        onSuccess();
      })
      .catch((error) => {
        notify({
          type: "error",
          message: error?.message || text.uploadAttachmentsError,
        });
      })
      .finally(() => {
        setLoading(false);
        handleOnCancel();
      });
  };

  return (
    <Modal
      title={text.uploadAttachments}
      visible={isOpen}
      onCancel={handleOnCancel}
      footer={[
        <Button key="cancel" onClick={handleOnCancel}>
          {text.cancelButton}
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={loading}
          onClick={handleUpload}
        >
          {text.uploadText}
        </Button>,
      ]}
    >
      <Space direction="vertical" style={{ width: "100%" }}>
        <DocumentUploader
          setFileList={setFileList}
          fileList={fileList}
          multiple={false}
          name="file_attachment"
        />
        <Input.TextArea
          rows={4}
          placeholder={text.uploadAttachmentsComment}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />
      </Space>
    </Modal>
  );
};

export default UploadAttachmentModal;
