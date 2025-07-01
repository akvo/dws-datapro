import React, { useMemo } from "react";
import { Upload } from "antd";
import { FileTextFilled } from "@ant-design/icons";
import { config, store, uiText } from "../lib";
import { useNotification } from "../util/hooks";

const { Dragger } = Upload;

const DocumentUploader = ({
  setFileList,
  fileList = [],
  multiple = true,
  name = "files",
}) => {
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const { notify } = useNotification();

  return (
    <Dragger
      name={name}
      multiple={multiple} // Allow multiple files if not editing
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
      maxCount={multiple ? null : 1}
    >
      <p className="ant-upload-drag-icon">
        <FileTextFilled style={{ color: "#666666", fontSize: 64 }} />
      </p>
      <p style={{ fontSize: 14 }}>{text.batchFilesHint}</p>
    </Dragger>
  );
};

export default DocumentUploader;
