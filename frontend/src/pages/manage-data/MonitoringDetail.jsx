import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
  useContext,
} from "react";
import "./style.scss";
import {
  Row,
  Col,
  Divider,
  Table,
  Typography,
  ConfigProvider,
  Empty,
  Modal,
  Button,
  Space,
  Dropdown,
  Tabs,
  Select,
  Tag,
  Tooltip,
} from "antd";
import {
  LeftCircleOutlined,
  DownCircleOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  FormOutlined,
} from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { api, store, uiText } from "../../lib";
import DataDetail from "./DataDetail";
import { Breadcrumbs, DescriptionPanel } from "../../components";
import { useNotification } from "../../util/hooks";
import { AbilityContext } from "../../components/can";

const { Title } = Typography;
const { TabPane } = Tabs;

const MonitoringDetail = () => {
  const { form, parentId } = useParams();
  const navigate = useNavigate();

  const { language, selectedFormData } = store.useState((s) => s);
  const childrenForms = useMemo(() => {
    return window?.forms?.filter((f) => `${f.content?.parent}` === form);
  }, [form]);
  // Get form_id from URL as default selectedForm
  const formIdFromUrl = new URLSearchParams(window.location.search).get(
    "form_id"
  );
  const defaultFormId = formIdFromUrl
    ? parseInt(formIdFromUrl, 10)
    : childrenForms[0]?.id;

  const { notify } = useNotification();
  const [loading, setLoading] = useState(false);
  const [dataset, setDataset] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [updateRecord, setUpdateRecord] = useState(
    formIdFromUrl ? true : false
  );
  const [deleteData, setDeleteData] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [editedRecord, setEditedRecord] = useState({});
  const [dataTab, setDataTab] = useState(
    formIdFromUrl ? "monitoring-data" : "registration-data"
  );
  const [selectedForm, setSelectedForm] = useState(defaultFormId);
  const ability = useContext(AbilityContext);

  const editable = ability.can("edit", "data");

  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const pagePath = [
    {
      title: text.controlCenter,
      link: "/control-center",
    },
    {
      title: text.manageDataTitle,
      link: "/control-center/data",
    },
    {
      title: text.monitoringDataTitle,
    },
  ];

  const { questionGroups } = store.useState((state) => state);

  const columns = [
    {
      title: text.lastUpdatedCol,
      dataIndex: "updated",
      render: (cell, row) => cell || row.created,
    },
    {
      title: text.nameCol,
      dataIndex: "name",
      key: "name",
    },
    {
      title: text.channelCol,
      dataIndex: "submitter",
      render: (submitter) =>
        submitter ? (
          <Tooltip title={submitter}>
            <Tag color="green">{text.mobileAppText}</Tag>
          </Tooltip>
        ) : (
          <Tag color="blue">{text.webformText}</Tag>
        ),
    },
    {
      title: text.userCol,
      dataIndex: "created_by",
    },
    Table.EXPAND_COLUMN,
  ];

  const handleChange = (e) => {
    setCurrentPage(e.current);
  };

  const handleDeleteData = () => {
    if (deleteData?.id) {
      setDeleting(true);
      api
        .delete(`data/${deleteData.id}`)
        .then(() => {
          notify({
            type: "success",
            message: `${deleteData.name} deleted`,
          });
          setDataset(dataset.filter((d) => d.id !== deleteData.id));
          setDeleteData(null);
        })
        .catch((err) => {
          notify({
            type: "error",
            message: "Could not delete datapoint",
          });
          console.error(err.response);
        })
        .finally(() => {
          setDeleting(false);
        });
    }
  };

  const goToMonitoringForm = async (form) => {
    const { uuid } = selectedFormData;
    navigate(`/control-center/form/${form}/${uuid}`);
  };

  useEffect(() => {
    if (questionGroups.length === 0 && dataset.length > 0) {
      store.update((s) => {
        s.questionGroups = window.forms.find(
          (f) => f.id === dataset[0]?.form
        ).content.question_group;
      });
    }
  }, [questionGroups, dataset]);

  const fetchDatapoint = useCallback(async () => {
    if (parentId) {
      const { data: apiData } = await api.get(`/data-details/${parentId}`);
      store.update((s) => {
        s.selectedFormData = apiData;
      });
    }
  }, [parentId]);

  useEffect(() => {
    fetchDatapoint();
  }, [fetchDatapoint]);

  const fetchMonitoringData = useCallback(async () => {
    try {
      if (updateRecord && selectedFormData?.uuid) {
        setUpdateRecord(false);

        setLoading(true);
        const parentUUID = selectedFormData?.uuid;
        const url = `/form-data/${selectedForm}/?page=${currentPage}&parent=${parentUUID}`;
        const { data: apiData } = await api.get(url);
        const { data: dataList, total } = apiData || {};
        setDataset(dataList);
        setTotalCount(total);
        setLoading(false);
      }
    } catch {
      setUpdateRecord(false);
      setLoading(false);
    }
  }, [currentPage, updateRecord, selectedForm, selectedFormData?.uuid]);

  useEffect(() => {
    fetchMonitoringData();
  }, [fetchMonitoringData]);

  return (
    <div id="manageData">
      <div className="description-container">
        <Row justify="space-between">
          <Col>
            <Breadcrumbs pagePath={pagePath} />
            <DescriptionPanel
              description={text.monitoringDataDescription}
              title={text.monitoringDataTitle}
            />
          </Col>
        </Row>
      </div>

      <div className="table-section">
        <div className="table-wrapper">
          <Row justify={"space-between"} align={"middle"}>
            <Col span={6}>
              <Button
                shape="round"
                onClick={() => navigate("/control-center/data")}
                icon={<ArrowLeftOutlined />}
              >
                {text.backManageData}
              </Button>
            </Col>
            <Col span={6} style={{ textAlign: "right" }}>
              <Dropdown
                trigger={["click"]}
                menu={{
                  items: childrenForms.map((form) => ({
                    key: form.id,
                    label: form.name,
                  })),
                  onClick: (e) => goToMonitoringForm(e.key),
                }}
              >
                <Button type="primary" shape="round" icon={<FormOutlined />}>
                  {text.updateDataButton}
                </Button>
              </Dropdown>
            </Col>
          </Row>
          <Divider />
          <Title>{selectedFormData?.name || text.loadingText}</Title>
          <div
            style={{ padding: "16px 0 0", minHeight: "40vh" }}
            bodystyle={{ padding: 0 }}
          >
            <Tabs
              className="manage-data-tab"
              activeKey={dataTab}
              onChange={(activeKey) => {
                if (activeKey === "monitoring-data") {
                  setUpdateRecord(true);
                }
                setDataTab(activeKey);
              }}
            >
              <TabPane tab={text.manageDataTab1} key="registration-data">
                <DataDetail
                  record={selectedFormData}
                  updateRecord={updateRecord}
                  updater={setUpdateRecord}
                  setDeleteData={setDeleteData}
                  setEditedRecord={setEditedRecord}
                  editedRecord={editedRecord}
                  isPublic={editable}
                  isFullScreen
                />
              </TabPane>
              <TabPane tab={text.manageDataTab2} key="monitoring-data">
                <Row style={{ marginBottom: "16px" }}>
                  <Col flex={1}>
                    <Select
                      value={selectedForm}
                      onChange={(value) => {
                        setSelectedForm(value);
                        setUpdateRecord(true);
                        setCurrentPage(1);
                      }}
                      fieldNames={{ label: "name", value: "id" }}
                      options={childrenForms}
                      placeholder={text.selectFormPlaceholder}
                    />
                  </Col>
                </Row>
                <ConfigProvider
                  renderEmpty={() => <Empty description={text.noFormText} />}
                >
                  <Table
                    columns={columns}
                    dataSource={dataset}
                    loading={loading}
                    onChange={handleChange}
                    pagination={{
                      current: currentPage,
                      total: totalCount,
                      pageSize: 10,
                      showSizeChanger: false,
                      showTotal: (total, range) =>
                        `Results: ${range[0]} - ${range[1]} of ${total} data`,
                    }}
                    rowKey="id"
                    expandable={{
                      expandedRowRender: (record) => (
                        <DataDetail
                          record={record}
                          updateRecord={updateRecord}
                          updater={setUpdateRecord}
                          setDeleteData={setDeleteData}
                          setEditedRecord={setEditedRecord}
                          editedRecord={editedRecord}
                          isPublic={editable}
                        />
                      ),
                      expandIcon: ({ expanded, onExpand, record }) =>
                        expanded ? (
                          <DownCircleOutlined
                            onClick={(e) => onExpand(record, e)}
                            style={{ color: "#1651B6", fontSize: "19px" }}
                          />
                        ) : (
                          <LeftCircleOutlined
                            onClick={(e) => onExpand(record, e)}
                            style={{ color: "#1651B6", fontSize: "19px" }}
                          />
                        ),
                    }}
                    rowClassName={(record) => {
                      const rowEdited = editedRecord[record.id]
                        ? "row-edited"
                        : "row-normal sticky";
                      return `expandable-row ${rowEdited}`;
                    }}
                    expandRowByClick
                  />
                </ConfigProvider>
              </TabPane>
            </Tabs>
          </div>
        </div>
      </div>
      <Modal
        open={deleteData}
        onCancel={() => setDeleteData(null)}
        centered
        width="575px"
        footer={
          <Row justify="center" align="middle">
            <Col span={14}>&nbsp;</Col>
            <Col span={10}>
              <Button
                className="light"
                disabled={deleting}
                onClick={() => {
                  setDeleteData(null);
                }}
              >
                {text.cancelButton}
              </Button>
              <Button
                type="primary"
                danger
                loading={deleting}
                onClick={handleDeleteData}
              >
                {text.deleteText}
              </Button>
            </Col>
          </Row>
        }
        bodystyle={{ textAlign: "center" }}
      >
        <Space direction="vertical">
          <DeleteOutlined style={{ fontSize: "50px" }} />
          <p>
            You are about to delete <i>{`${deleteData?.name}`}</i> data.{" "}
            <b>Delete a datapoint also will delete the history</b>. Are you sure
            want to delete this datapoint?
          </p>
        </Space>
      </Modal>
    </div>
  );
};

export default React.memo(MonitoringDetail);
