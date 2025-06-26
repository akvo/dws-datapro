import React, { useMemo, useState, useEffect } from "react";
import { Table, Tabs, Row, Button, Col } from "antd";
import {
  LeftCircleOutlined,
  DownCircleOutlined,
  FileTextFilled,
} from "@ant-design/icons";
import {
  ApproverDetailTable,
  CreateBatchModal,
  DataFilters,
} from "../../../components";
import { api, columnsBatch, store, uiText } from "../../../lib";
import { Link } from "react-router-dom";
import { useNotification } from "../../../util/hooks";
import { isEmpty, without, union, xor } from "lodash";

const { TabPane } = Tabs;

const columnsPending = [
  {
    title: "Name",
    dataIndex: "name",
    key: "name",
    render: (name, row) => (
      <Row align="middle">
        <Col style={{ marginRight: 20 }}>
          <FileTextFilled style={{ color: "#666666", fontSize: 28 }} />
        </Col>
        <Col>
          <div>{name}</div>
          <div>{row.created}</div>
        </Col>
      </Row>
    ),
  },
  {
    title: "Administration",
    dataIndex: "administration",
    key: "administration",
    width: 200,
  },
  {
    title: "Submitter Name",
    dataIndex: "submitter",
    key: "submitter",
    render: (submitter, dt) => {
      return submitter || dt.created_by;
    },
    width: 200,
  },
  {
    title: "Duration",
    dataIndex: "duration",
    key: "duration",
    render: (duration) => duration || "",
    align: "center",
    width: 100,
  },
];

const PanelSubmissions = () => {
  const [dataset, setDataset] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedRows, setSelectedRows] = useState([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [selectedTab, setSelectedTab] = useState("pending-data");
  const [modalButton, setModalButton] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const { notify } = useNotification();
  const { selectedForm, user } = store.useState((state) => state);

  useEffect(() => {
    let url = `form-pending-data/${selectedForm}/?page=${currentPage}`;
    if (selectedTab === "pending-data") {
      setExpandedKeys([]);
      setModalButton(true);
    }
    if (selectedTab === "pending-batch") {
      url = `batch/?form=${selectedForm}&page=${currentPage}`;
      setModalButton(false);
    }
    if (selectedTab === "approved-batch") {
      url = `batch/?form=${selectedForm}&page=${currentPage}&approved=true`;
      setModalButton(false);
    }
    if (
      selectedTab === "pending-batch" ||
      selectedTab === "approved-batch" ||
      selectedForm
    ) {
      setLoading(true);
      api
        .get(url)
        .then((res) => {
          setDataset(res.data.data);
          setTotalCount(res.data.total);
          setLoading(false);
        })
        .catch(() => {
          setDataset([]);
          setTotalCount(0);
          setLoading(false);
        });
    }
  }, [selectedTab, selectedForm, currentPage]);

  useEffect(() => {
    if (selectedForm) {
      setSelectedRows([]);
      setSelectedRowKeys([]);
    }
  }, [selectedForm]);

  useEffect(() => {
    if (selectedTab) {
      setDataset([]);
    }
  }, [selectedTab]);

  useEffect(() => {
    if (dataset.length) {
      const selectedDataset = selectedRowKeys.map((s) => {
        const findData = dataset.find((d) => d.id === s);
        return findData;
      });
      setSelectedRows(selectedDataset);
    }
  }, [dataset, selectedRowKeys]);

  const handlePageChange = (e) => {
    setCurrentPage(e.current);
  };

  const hasSelected = !isEmpty(selectedRowKeys);
  const onSelectTableRow = (val) => {
    const { id } = val;
    selectedRowKeys.includes(id)
      ? setSelectedRowKeys(without(selectedRowKeys, id))
      : setSelectedRowKeys([...selectedRowKeys, id]);
  };

  const onSelectAllTableRow = (isSelected) => {
    const ids = dataset.filter((x) => !x?.disabled).map((x) => x.id);
    if (!isSelected && hasSelected) {
      setSelectedRowKeys(xor(selectedRowKeys, ids));
    }
    if (isSelected && !hasSelected) {
      setSelectedRowKeys(ids);
    }
    if (isSelected && hasSelected) {
      setSelectedRowKeys(union(selectedRowKeys, ids));
    }
  };

  const btnBatchSelected = useMemo(() => {
    const handleOnClickBatchSelectedDataset = () => {
      // check only for data entry role
      if (!user.is_superuser) {
        api.get(`form/check-approver/${selectedForm}`).then((res) => {
          if (!res.data.count) {
            notify({
              type: "error",
              message: text.batchNoApproverMessage,
            });
          } else {
            setModalVisible(true);
          }
        });
      } else {
        setModalVisible(true);
      }
    };
    if (!!selectedRows.length && modalButton) {
      return (
        <Button
          type="primary"
          shape="round"
          onClick={handleOnClickBatchSelectedDataset}
        >
          {text.batchSelectedDatasets}
        </Button>
      );
    }
    return "";
  }, [
    selectedRows,
    modalButton,
    text.batchSelectedDatasets,
    notify,
    selectedForm,
    text.batchNoApproverMessage,
    user.is_superuser,
  ]);

  const DataTable = ({ pane }) => {
    return (
      <Table
        loading={loading}
        dataSource={dataset}
        columns={
          pane === "pending-data"
            ? [...columnsPending]
            : [...columnsBatch, Table.EXPAND_COLUMN]
        }
        onChange={handlePageChange}
        rowSelection={
          pane === "pending-data"
            ? {
                selectedRowKeys: selectedRowKeys,
                onSelect: onSelectTableRow,
                onSelectAll: onSelectAllTableRow,
                getCheckboxProps: (record) => ({
                  disabled: record?.disabled,
                }),
              }
            : false
        }
        pagination={{
          current: currentPage,
          total: totalCount,
          pageSize: 10,
          showSizeChanger: false,
          showTotal: (total, range) =>
            `Results: ${range[0]} - ${range[1]} of ${total} data`,
        }}
        rowKey="id"
        expandedRowKeys={expandedKeys}
        expandable={
          pane === "pending-data"
            ? false
            : {
                expandedRowRender: (record) => (
                  <ApproverDetailTable data={record?.approvers} />
                ),
                expandIcon: (expand) => {
                  return expand.expanded ? (
                    <DownCircleOutlined
                      onClick={() => setExpandedKeys([])}
                      style={{ color: "#1651B6", fontSize: "19px" }}
                    />
                  ) : (
                    <LeftCircleOutlined
                      onClick={() => setExpandedKeys([expand.record.id])}
                      style={{ color: "#1651B6", fontSize: "19px" }}
                    />
                  );
                },
              }
        }
        rowClassName={pane === "pending-data" ? null : "expandable-row"}
        expandRowByClick
      />
    );
  };

  return (
    <>
      <div id="panel-submission">
        <h1 className="submission">Submissions</h1>
        <DataFilters showAdm={false} />
        <Tabs
          activeKey={selectedTab}
          defaultActiveKey={selectedTab}
          onChange={setSelectedTab}
          tabBarExtraContent={btnBatchSelected}
        >
          <TabPane tab={text.uploadsTab1} key={"pending-data"}>
            <DataTable pane="pending-data" />
          </TabPane>
          <TabPane tab={text.uploadsTab2} key={"pending-batch"}>
            <DataTable pane="pending-batch" />
          </TabPane>
          <TabPane tab={text.uploadsTab3} key={"approved-batch"}>
            <DataTable pane="approved-batch" />
          </TabPane>
        </Tabs>
        <Link to="/control-center/data/submissions">
          <Button className="view-all" type="primary" shape="round">
            View All
          </Button>
        </Link>
      </div>
      <CreateBatchModal
        selectedRows={selectedRows}
        isOpen={modalVisible}
        onCancel={() => {
          setModalVisible(false);
        }}
        onSuccess={() => {
          setSelectedRows([]);
          setSelectedRowKeys([]);
          setSelectedTab("pending-batch");
          setModalVisible(false);
        }}
      />
    </>
  );
};

export default PanelSubmissions;
