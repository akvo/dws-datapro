import React, { useState, useMemo } from "react";
import {
  Table,
  Checkbox,
  Button,
  Modal,
  Row,
  Col,
  Input,
  Upload,
  Divider,
  Space,
} from "antd";
import { FileTextFilled } from "@ant-design/icons";
import { api, config, store, uiText } from "../lib";
import { useNotification } from "../util/hooks";

const { TextArea } = Input;
const { Dragger } = Upload;

const CreateBatchModal = ({
  onCancel,
  onSuccess,
  isOpen = false,
  selectedRows = [],
}) => {
  const [loading, setLoading] = useState(false);
  const [batchName, setBatchName] = useState("");
  const [comment, setComment] = useState("");
  const [fileList, setFileList] = useState([]);

  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const { notify } = useNotification();

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const sendBatch = () => {
    setLoading(true);

    // Always use FormData for consistency
    const formData = new FormData();
    formData.append("name", batchName);

    // Add data IDs as JSON string
    selectedRows.forEach((row, rx) => {
      formData.append(`data[${rx}]`, row.id);
    });

    // Add comment if present
    if (comment.length) {
      formData.append("comment", comment);
    }

    // Append files if any exist
    if (fileList.length) {
      fileList.forEach((file, index) => {
        formData.append(`files[${index}]`, file.originFileObj);
      });
    }

    // Send with FormData and proper headers
    api
      .post("batch", formData)
      .then(() => {
        setBatchName("");
        setComment("");
        setFileList([]);
        if (typeof onSuccess === "function") {
          onSuccess();
        }
      })
      .catch(() => {
        notify({
          type: "error",
          message: text.notifyError,
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleOnCancel = () => {
    setFileList([]);
    setBatchName("");
    setComment("");
    if (typeof onCancel === "function") {
      onCancel();
    }
  };

  return (
    <Modal
      open={isOpen}
      onCancel={handleOnCancel}
      maskClosable={false}
      footer={
        <Row align="middle">
          <Col xs={8} align="left">
            <Checkbox checked={true} disabled={true} className="dev">
              {text.sendNewRequest}
            </Checkbox>
          </Col>
          <Col xs={16}>
            <Space>
              <Button className="light" shape="round" onClick={handleOnCancel}>
                {text.cancelButton}
              </Button>
              <Button
                type="primary"
                shape="round"
                onClick={sendBatch}
                disabled={!batchName?.trim()?.length}
                loading={loading}
              >
                {text.createNewBatch}
              </Button>
            </Space>
          </Col>
        </Row>
      }
    >
      <p>{text.batchHintText}</p>
      <p>
        <FileTextFilled style={{ color: "#666666", fontSize: 64 }} />
      </p>
      <p>{text.batchHintDesc}</p>
      <Table
        bordered
        size="small"
        dataSource={selectedRows}
        columns={[
          {
            title: "Dataset",
            dataIndex: "name",
            key: "name",
          },
          {
            title: "Date Uploaded",
            dataIndex: "created",
            key: "created",
            align: "right",
          },
        ]}
        pagination={false}
        scroll={{ y: 270 }}
        rowKey="id"
      />
      <Divider />
      <Row align="middle">
        <Col xs={24} align="left">
          <div className="batch-name-field">
            <label>{text.batchName}</label>
            <Input
              onChange={(e) => {
                // Ensure batch name is trimmed and not empty
                setBatchName(e.target.value);
              }}
              allowClear
              value={batchName || ""}
            />
          </div>
          <label>{text.submissionComment}</label>
          <TextArea
            rows={4}
            onChange={(e) => setComment(e.target.value)}
            value={comment}
          />
          <Dragger
            name="files"
            multiple={true}
            accept={config.batchAttachment.allowed.join(",")}
            beforeUpload={(file) => {
              const fileMB = file.size / (1024 * 1024);
              const isAllowed =
                config.batchAttachment.allowed.includes(file.type) &&
                fileMB <= config.batchAttachment.maxSize;
              if (!isAllowed) {
                notify({
                  type: "error",
                  message: text.batchFileTypeError,
                });
              }
              return isAllowed || Upload.LIST_IGNORE;
            }}
            onChange={(info) => {
              if (info.fileList.length > 0) {
                setFileList(info.fileList);
              }
            }}
            onRemove={(file) => {
              setFileList((prevFileList) =>
                prevFileList.filter((f) => f.uid !== file.uid)
              );
            }}
            fileList={fileList}
            customRequest={({ onSuccess }) => {
              onSuccess("ok");
            }}
          >
            <p className="ant-upload-drag-icon">
              <FileTextFilled style={{ color: "#666666", fontSize: 64 }} />
            </p>
            <p style={{ fontSize: 14 }}>{text.batchFilesHint}</p>
          </Dragger>
        </Col>
      </Row>
    </Modal>
  );
};

export default CreateBatchModal;
