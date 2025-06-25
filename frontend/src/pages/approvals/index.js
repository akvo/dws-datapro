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
    render: (approvers) => {
      if (approvers?.length === 0) {
        return <span>No approver assigned</span>;
      }
      return (
        <div>
          <ul style={{ paddingLeft: "20px", margin: 0 }}>
            {approvers.map((approver, index) => {
              const level = levels.find(
                (l) => l.level === approver.administration_level
              );
              return (
                <li key={index}>
                  <Space>
                    {level && <strong>({level.name})</strong>}
                    <span>{approver.name}</span>
                  </Space>
                </li>
              );
            })}
          </ul>
        </div>
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
