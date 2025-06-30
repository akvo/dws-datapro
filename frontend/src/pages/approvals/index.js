import { Row, Col, Tag, Space } from "antd";
import {
  FileTextFilled,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";

export const columnsApproval = (levels) => [
  {
    title: "Submission",
    dataIndex: "name",
    key: "name",
    render: (filename, row) => (
      <Row align="middle">
        <Col style={{ marginRight: 20 }}>
          <FileTextFilled style={{ color: "#666666", fontSize: 28 }} />
        </Col>
        <Col>
          <div>{filename}</div>
          <div>{row.created}</div>
        </Col>
      </Row>
    ),
  },
  {
    title: "Form",
    dataIndex: "form",
    key: "form",
    render: (form) => form.name,
  },
  {
    title: "Submitter",
    dataIndex: "created_by",
    key: "created_by",
    width: 140,
  },
  {
    title: "Total Data",
    align: "center",
    dataIndex: "total_data",
    key: "total_data",
    width: 140,
  },
  {
    title: "Location",
    dataIndex: "administration",
    key: "administration",
    render: (administration) => administration.name,
    width: 140,
  },
  {
    title: "Waiting on",
    align: "center",
    dataIndex: "approver",
    key: "approver",
    render: (approvers, { approved }) => {
      if (approvers?.length === 0) {
        if (approved) {
          return <span>All approvers already approved</span>;
        }
        return <span>No approver assigned</span>;
      }
      const names = approvers.map((a) => a.name);
      const maxNames = 3;
      const displayedNames = names.slice(0, maxNames);
      const remainingCount = names.length - maxNames;
      const displayText =
        displayedNames.length > 0
          ? displayedNames.join(", ") +
            (remainingCount > 0 ? ` and ${remainingCount} more` : "")
          : "No approver assigned";
      return (
        <Space direction="vertical" style={{ width: "100%" }}>
          <p style={{ margin: 0 }}>{displayText}</p>
        </Space>
      );
    },
    width: 180,
  },
  {
    title: "Status",
    align: "center",
    dataIndex: "approved",
    key: "approved",
    render: (_, record) => {
      const allowApprove = record?.approver?.some((a) => a?.allow_approve);
      return (
        <span>
          <Tag
            icon={
              allowApprove ? <ClockCircleOutlined /> : <CheckCircleOutlined />
            }
            color={allowApprove ? "default" : "success"}
          >
            {allowApprove ? "Pending" : "Approved"}
          </Tag>
        </span>
      );
    },
    width: 180,
  },
];
