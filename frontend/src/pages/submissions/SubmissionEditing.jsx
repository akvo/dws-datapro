import React, { useMemo } from "react";
import { Button, Space, Spin, Modal } from "antd";
import { LoadingOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { RawDataTable } from "../../components";
import { store, uiText } from "../../lib";

const { confirm } = Modal;

const SubmissionEditing = ({
  expanded,
  updateCell,
  resetCell,
  handleSave,
  saving,
  dataLoading,
  isEdited,
  isEditable,
  handleDelete,
  deleting,
  resetButton,
}) => {
  const language = store.useState((s) => s.language);
  const { active: activeLang } = language;

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  if (expanded.loading) {
    return (
      <Space style={{ paddingTop: 18, color: "#9e9e9e" }} size="middle">
        <Spin
          indicator={<LoadingOutlined style={{ color: "#1b91ff" }} spin />}
        />
        <span>{text.loading}</span>
      </Space>
    );
  }

  return (
    <>
      <div className={`pending-data-outer`}>
        {expanded.data?.map((r, rI) => (
          <div className="pending-data-wrapper" key={rI}>
            <h3>{r.label}</h3>
            <RawDataTable
              updateCell={updateCell}
              resetCell={resetCell}
              dataLoading={dataLoading}
              isEditable={isEditable}
              resetButton={resetButton}
              expanded={expanded}
              questions={r.question}
            />
          </div>
        ))}
      </div>
      {isEditable && !expanded.loading && (
        <div className="pending-data-actions" style={{ padding: "1rem" }}>
          <Button
            type="primary"
            shape="round"
            onClick={() => handleSave(expanded)}
            loading={expanded.id === saving}
            disabled={expanded.id === dataLoading || isEdited() === false}
          >
            {text.saveEditButton}
          </Button>
          <Button
            danger
            shape="round"
            style={{ marginLeft: "10px" }}
            disabled={deleting}
            onClick={() => {
              confirm({
                title: "Are you sure to delete this batch?",
                icon: <ExclamationCircleOutlined />,
                content: "Once you have deleted you can't get it back",
                okText: "Yes",
                okType: "danger",
                cancelText: "No",
                onOk() {
                  handleDelete(expanded);
                },
                onCancel() {
                  return;
                },
              });
            }}
          >
            {text.deleteText}
          </Button>
        </div>
      )}
    </>
  );
};

export default SubmissionEditing;
