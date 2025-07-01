import React, { useState, useMemo, useEffect, useCallback } from "react";

import { Modal, Button, Input, Space, Typography } from "antd";
import { api, store, uiText } from "../../lib";
import { useNotification } from "../../util/hooks";
import { DocumentUploader } from "../../components";

const { Text, Title } = Typography;

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
  const [isEmpty, setIsEmpty] = useState(false);
  const [preload, setPreload] = useState(true);

  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);
  const { notify } = useNotification();

  const handleOnCancel = () => {
    setPreload(true);
    setIsEmpty(false);
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
      formData.append("file", file.originFileObj);
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
        setLoading(false);
        handleOnCancel();
      })
      .catch((error) => {
        setLoading(false);
        if (error.response?.status === 400) {
          setIsEmpty(true);
        } else {
          const { detail } = error.response?.data || {};
          notify({
            type: "error",
            message: detail?.file?.[0] || text.uploadAttachmentsError,
          });
        }
        return;
      });
  };

  const fetchEditFile = useCallback(() => {
    if (fileList.length === 0 && preload && editData?.file_path) {
      setPreload(false);
      fetch(editData.file_path)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.blob();
        })
        .then((blob) => {
          const file = new File([blob], editData.name, {
            type: editData.file_type || "application/octet-stream",
          });
          setFileList([
            {
              uid: editData.id,
              name: editData.name,
              status: "done",
              url: editData.file_path,
              originFileObj: file,
            },
          ]);
        })
        .catch((error) => {
          console.error("Error fetching file:", error);
        });
    }
  }, [fileList, preload, editData]);

  useEffect(() => {
    fetchEditFile();
  }, [fetchEditFile]);

  return (
    <Modal
      title={
        <Space direction="vertical" style={{ width: "100%" }}>
          <Title level={5} style={{ margin: 0 }}>
            {editData?.id ? text.editAttachment : text.addAttachment}
          </Title>
          <Text type="secondary">
            {editData?.id ? text.editAttachmentDesc : text.addAttachmentDesc}
          </Text>
        </Space>
      }
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
        <div
          style={{
            width: "100%",
            borderColor: isEmpty ? "#ef7575" : "transparent",
            borderWidth: isEmpty ? 1 : 0,
            borderStyle: isEmpty ? "solid" : "hidden",
          }}
        >
          <DocumentUploader
            setFileList={(files) => {
              if (isEmpty) {
                setIsEmpty(false);
              }
              setFileList(files);
            }}
            fileList={fileList}
            multiple={false}
            name="file"
          />
        </div>
        {isEmpty && (
          <i style={{ fontSize: 12, color: "#ef7575" }}>
            {text.uploadAttachmentsRequired}
          </i>
        )}
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
