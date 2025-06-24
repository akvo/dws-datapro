import React from "react";
import { Table, Tag } from "antd";
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";

const ApproverDetailTable = ({ data = [] }) => {
  const columnsApprover = [
    {
      title: "Approver",
      dataIndex: "names",
      key: "names",
      render: (names) => (
        <ul style={{ paddingLeft: "20px", margin: 0 }}>
          {names?.map((name, index) => (
            <li key={index}>{name}</li>
          ))}
        </ul>
      ),
    },
    {
      title: "Administration",
      dataIndex: "administration",
      key: "administration",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => {
        let finalStatus = "Pending";
        let icon = <ClockCircleOutlined />;
        let color = "default";

        if (status.includes("Rejected")) {
          finalStatus = "Rejected";
          icon = <CloseCircleOutlined />;
          color = "error";
        } else if (status.includes("Approved")) {
          finalStatus = "Approved";
          icon = <CheckCircleOutlined />;
          color = "success";
        }

        return (
          <span>
            <Tag icon={icon} color={color}>
              {finalStatus}
            </Tag>
          </span>
        );
      },
    },
  ];

  // Group dataSource by administration
  const groupedData = data?.reduce((acc, item) => {
    const existingGroup = acc.find(
      (group) => group.administration === item.administration
    );

    if (existingGroup) {
      existingGroup.names.push(item.name);
      existingGroup.status.push(item.status_text);
    } else {
      acc.push({
        key: acc.length,
        administration: item.administration,
        names: [item.name],
        status: [item.status_text],
      });
    }

    return acc;
  }, []);

  return (
    <Table
      columns={columnsApprover}
      dataSource={groupedData}
      rowClassName="expandable-row"
      pagination={false}
    />
  );
};

export default ApproverDetailTable;
