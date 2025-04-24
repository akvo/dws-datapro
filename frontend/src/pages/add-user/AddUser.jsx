import React, { useState, useEffect, useMemo } from "react";
import "./style.scss";
import {
  Row,
  Col,
  Form,
  Button,
  Input,
  Select,
  Checkbox,
  Modal,
  Table,
  Collapse,
  Space,
  Spin,
} from "antd";
import { AdministrationDropdown } from "../../components";
import { useNavigate, useParams } from "react-router-dom";
import {
  api,
  store,
  config,
  uiText,
  ROLE_ID_ADMIN,
  ROLE_ID_SUPERADMIN,
  FORM_ACCESS_ID_READ,
  FORM_ACCESS_ID_APPROVER,
} from "../../lib";
import { Breadcrumbs, DescriptionPanel } from "../../components";
import { takeRight, take } from "lodash";
import { useNotification } from "../../util/hooks";

const { Option } = Select;
const { Panel } = Collapse;

const descriptionData = (
  <p>
    This page allows you to add users to the RUSH platform.You will only be able
    to add users for regions under your jurisdisction.
    <br />
    Once you have added the user, the user will be notified by email to set
    their password and access the platform
  </p>
);

const AddUser = () => {
  const {
    user: authUser,
    administration,
    forms: allForms,
    language,
    levels,
  } = store.useState((s) => s);
  const NATIONAL_LEVEL = levels?.find((l) => l.level === 0)?.id;
  const { active: activeLang } = language;
  const forms = allForms.map((f) => ({
    ...f,
    access: config.accessFormTypes,
  }));

  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [adminError, setAdminError] = useState(null);
  const [levelError, setLevelError] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { notify } = useNotification();
  const { id } = useParams();
  const [organisations, setOrganisations] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalContent, setModalContent] = useState([]);
  const [isUserFetched, setIsUserFetched] = useState(false);

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);
  const panelTitle = id ? text.editUser : text.addUser;

  useEffect(() => {
    if (!organisations.length) {
      // filter by 1 for member attribute
      api.get("organisations?filter=1").then((res) => {
        setOrganisations(res.data);
      });
    }
  }, [organisations]);

  const pagePath = [
    {
      title: text.controlCenter,
      link: "/control-center",
    },
    {
      title: text.manageUsers,
      link: "/control-center/users",
    },
    {
      title: id ? text.editUser : text.addUser,
    },
  ];

  const onCloseModal = () => {
    setIsModalVisible(false);
    setModalContent([]);
  };

  const allowedRoles = useMemo(() => {
    const lookUp =
      authUser?.role?.id === ROLE_ID_SUPERADMIN
        ? ROLE_ID_SUPERADMIN
        : ROLE_ID_ADMIN;
    return config.roles.filter((r) => r.id >= lookUp);
  }, [authUser]);

  const setApproverForms = (data = []) => {
    return data.map((d) => ({
      ...d,
      access: d.access.map((a) => ({
        ...a,
        value: a.id === FORM_ACCESS_ID_APPROVER || a.id === FORM_ACCESS_ID_READ,
      })),
    }));
  };

  const onFinish = (values) => {
    setSubmitting(true);
    const admin = takeRight(administration, 1)?.[0];
    const formsPayload = values?.forms?.length
      ? values.forms
      : values.nationalApprover
      ? setApproverForms(forms)
      : [];
    const access_form = formsPayload
      .map((f) =>
        f.access
          .filter((f_access) => f_access.value)
          .map((f_access) => ({
            form_id: f.id,
            access_type: f_access.id,
          }))
      )
      .flat();
    const payload = {
      first_name: values.first_name,
      last_name: values.last_name,
      email: values.email,
      administration: admin.id,
      phone_number: values.phone_number,
      designation: values.designation,
      role: values.role,
      inform_user: values.inform_user,
      organisation: values.organisation,
      trained: values.trained,
      access_form: access_form,
    };
    api[id ? "put" : "post"](id ? `user/${id}` : "user", payload)
      .then(() => {
        notify({
          type: "success",
          message: `User ${id ? "updated" : "added"}`,
        });
        setSubmitting(false);
        navigate("/control-center/users");
      })
      .catch((err) => {
        if (err?.response?.status === 403) {
          setIsModalVisible(true);
          setModalContent(err?.response?.data?.message);
        } else {
          notify({
            type: "error",
            message:
              err?.response?.data?.message ||
              `User could not be ${id ? "updated" : "added"}`,
          });
        }
        setSubmitting(false);
      });
  };

  const onRoleChange = (r) => {
    setRole(r);
    setSelectedLevel(null);
    setLevelError(false);
    setAdminError(null);
    form.setFieldsValue({
      nationalApprover: false,
      forms: allForms.map((f) => ({
        ...f,
        access: config.accessFormTypes,
      })),
    });
    if (r > 1) {
      store.update((s) => {
        s.administration = take(s.administration, 1);
      });
    }
  };

  const onLevelChange = (l) => {
    setSelectedLevel(l);
    setLevelError(false);
    setAdminError(null);
    if (administration.length >= l) {
      store.update((s) => {
        s.administration.length = l;
      });
    }
  };

  const onAdminChange = () => {
    setLevelError(false);
    setAdminError(null);
  };

  const onNationalApproverChange = (e) => {
    const isChecked = e.target.checked;
    if (isChecked) {
      const forms = form.getFieldValue("forms");
      const updatedForms = setApproverForms(forms);
      form.setFieldsValue({ forms: updatedForms });
    } else {
      form.setFieldsValue({
        forms,
      });
    }
  };

  useEffect(() => {
    const fetchData = async (adminId, acc, roleRes) => {
      const adm = await config.fn.administration(adminId);
      acc.unshift(adm);
      if (adm.level > 0) {
        fetchData(adm.parent, acc, roleRes);
      } else {
        store.update((s) => {
          s.administration = acc;
        });
      }
    };
    if (id && !isUserFetched) {
      setIsUserFetched(true);
      setLoading(true);
      try {
        api.get(`user/${id}`).then((res) => {
          form.setFieldsValue({
            administration: res.data?.administration,
            designation: parseInt(res.data?.designation) || null,
            email: res.data?.email,
            first_name: res.data?.first_name,
            last_name: res.data?.last_name,
            phone_number: res.data?.phone_number,
            role: res.data?.role,
            forms: res.data?.forms.map((f) => parseInt(f.id)),
            organisation: res.data?.organisation?.id || [],
            trained: res?.data?.trained,
            // nationalApprover:
            //   res.data?.role === ROLE_ID_SUPERADMIN &&
            //   !!res.data?.forms?.length,
            inform_user: !id
              ? true
              : authUser?.email === res.data?.email
              ? false
              : true,
          });
          setRole(res.data?.role);
          setLoading(false);
          fetchData(res.data.administration, [], res.data?.role);
        });
      } catch (error) {
        notify({ type: "error", message: text.errorUserLoad });
        setLoading(false);
      }
    }
  }, [
    id,
    form,
    forms,
    notify,
    text.errorUserLoad,
    authUser?.email,
    isUserFetched,
  ]);

  return (
    <div id="add-user">
      <div className="description-container">
        <Row justify="space-between">
          <Col>
            <Breadcrumbs pagePath={pagePath} />
            <DescriptionPanel
              description={descriptionData}
              title={panelTitle}
            />
          </Col>
        </Row>
      </div>
      <div className="table-section">
        <div className="table-wrapper">
          <Spin tip={text.loadingText} spinning={loading}>
            <Form
              name="adm-form"
              form={form}
              labelCol={{ span: 6 }}
              wrapperCol={{ span: 18 }}
              initialValues={{
                first_name: "",
                last_name: "",
                phone_number: "",
                designation: null,
                email: "",
                role: null,
                inform_user: true,
                organisation: [],
                forms,
              }}
              onFinish={onFinish}
            >
              {(_, formInstance) => (
                <>
                  <div className="form-row">
                    <Form.Item
                      label={text.userFirstName}
                      name="first_name"
                      rules={[
                        {
                          required: true,
                          message: text.valFirstName,
                        },
                      ]}
                    >
                      <Input />
                    </Form.Item>
                  </div>
                  <div className="form-row">
                    <Form.Item
                      label={text.userLastName}
                      name="last_name"
                      rules={[
                        {
                          required: true,
                          message: text.valLastName,
                        },
                      ]}
                    >
                      <Input />
                    </Form.Item>
                  </div>
                  <div className="form-row">
                    <Form.Item
                      label={text.userEmail}
                      name="email"
                      rules={[
                        {
                          required: true,
                          message: text.valEmail,
                          type: "email",
                        },
                      ]}
                    >
                      <Input />
                    </Form.Item>
                  </div>
                  <div className="form-row">
                    <Form.Item
                      label={text.userPhoneNumber}
                      name="phone_number"
                      rules={[
                        {
                          required: true,
                          message: text.valPhone,
                        },
                      ]}
                    >
                      <Input />
                    </Form.Item>
                  </div>
                  <div className="form-row">
                    <Form.Item
                      name="organisation"
                      label={text.userOrganisation}
                      rules={[
                        { required: true, message: text.valOrganization },
                      ]}
                    >
                      <Select
                        getPopupContainer={(trigger) => trigger.parentNode}
                        placeholder={text.selectOne}
                        allowClear
                        showSearch
                        optionFilterProp="children"
                        filterOption={(input, option) =>
                          option.children
                            .toLowerCase()
                            .indexOf(input.toLowerCase()) >= 0
                        }
                      >
                        {organisations?.map((o, oi) => (
                          <Option key={`org-${oi}`} value={o.id}>
                            {o.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </div>
                  <div className="form-row">
                    <Form.Item
                      name="designation"
                      label={text.userDesignation}
                      rules={[{ required: true, message: text.valDesignation }]}
                    >
                      <Select
                        placeholder={text.selectOne}
                        getPopupContainer={(trigger) => trigger.parentNode}
                        showSearch
                        optionFilterProp="children"
                        filterOption={(input, option) =>
                          option.children
                            .toLowerCase()
                            .indexOf(input.toLowerCase()) >= 0
                        }
                      >
                        {config?.designations?.map((d, di) => (
                          <Option key={di} value={d.id}>
                            {d.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </div>
                  <Row className="form-row">
                    <Col span={18} offset={6}>
                      <Form.Item name="trained" valuePropName="checked">
                        <Checkbox>{text.userTrained}</Checkbox>
                      </Form.Item>
                    </Col>
                  </Row>
                  <div className="form-row">
                    <Form.Item
                      name="role"
                      label="Role"
                      rules={[{ required: true, message: text.valRole }]}
                    >
                      <Select
                        getPopupContainer={(trigger) => trigger.parentNode}
                        placeholder={text.selectOne}
                        onChange={onRoleChange}
                      >
                        {allowedRoles.map((r, ri) => (
                          <Option key={ri} value={r.id}>
                            {r.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </div>
                  <Row justify="center" align="middle">
                    <Col span={18} offset={6}>
                      {role && (
                        <span className="role-description">
                          {config.roles.find((r) => r.id === role)?.description}
                        </span>
                      )}
                    </Col>
                  </Row>
                  {role === ROLE_ID_ADMIN && (
                    <Form.Item label={text.admLevel}>
                      <Select
                        value={selectedLevel}
                        getPopupContainer={(trigger) => trigger.parentNode}
                        placeholder={text.selectOne}
                        onChange={onLevelChange}
                      >
                        {levels.map((l, li) => (
                          <Option key={li} value={l.id}>
                            {l.name}
                          </Option>
                        ))}
                      </Select>
                      {levelError && (
                        <div className="text-error">
                          {text.userSelectLevelRequired}
                        </div>
                      )}
                    </Form.Item>
                  )}
                  {role === ROLE_ID_ADMIN &&
                    selectedLevel &&
                    selectedLevel !== NATIONAL_LEVEL && (
                      <Row className="form-row">
                        <Col span={6} className=" ant-form-item-label">
                          <label htmlFor="administration">
                            {text.administrationLabel}
                          </label>
                        </Col>
                        <Col span={18}>
                          <AdministrationDropdown
                            withLabel={true}
                            persist={true}
                            size="large"
                            width="100%"
                            onChange={onAdminChange}
                            maxLevel={selectedLevel}
                          />
                          {!!adminError && (
                            <div className="text-error">{adminError}</div>
                          )}
                        </Col>
                      </Row>
                    )}
                  {(selectedLevel === NATIONAL_LEVEL ||
                    role === ROLE_ID_SUPERADMIN) && (
                    <Row justify="center" align="middle">
                      <Col span={18} offset={6}>
                        <div className="form-row">
                          <Form.Item
                            name="nationalApprover"
                            valuePropName="checked"
                            onChange={onNationalApproverChange}
                          >
                            <Checkbox>{text.userNationalApprover}</Checkbox>
                          </Form.Item>
                        </div>
                      </Col>
                    </Row>
                  )}

                  {(role === ROLE_ID_ADMIN ||
                    formInstance.getFieldValue("nationalApprover") ===
                      true) && (
                    <Row
                      justify="start"
                      align="stretch"
                      className="form-row"
                      style={{ marginTop: "24px" }}
                    >
                      <Col span={6} className=" ant-form-item-label">
                        <label htmlFor="forms">
                          {text.questionnairesLabel}
                        </label>
                      </Col>
                      <Col span={18}>
                        <Form.List name="forms">
                          {(fields) => (
                            <Collapse defaultActiveKey={["0"]}>
                              {fields.map(({ key, name, ...restField }) => (
                                <Panel
                                  key={key}
                                  header={form.getFieldValue([
                                    "forms",
                                    name,
                                    "name",
                                  ])}
                                  extra={
                                    <Space className="extra-access-label">
                                      {formInstance
                                        .getFieldValue([
                                          "forms",
                                          name,
                                          "access",
                                        ])
                                        .filter((a) => a?.value)
                                        .map((a) => (
                                          <span
                                            key={a.id}
                                            className="access-label"
                                          >
                                            {a.label}
                                          </span>
                                        ))}
                                    </Space>
                                  }
                                >
                                  <Form.Item
                                    {...restField}
                                    name={[name, "id"]}
                                    hidden
                                  >
                                    <Input />
                                  </Form.Item>
                                  <Form.List name={[name, "access"]}>
                                    {(accessFields) => (
                                      <ul
                                        style={{
                                          listStyle: "none",
                                          paddingLeft: 0,
                                        }}
                                      >
                                        {accessFields.map(
                                          ({
                                            key: accessKey,
                                            name: accessName,
                                            ...accessRestField
                                          }) => (
                                            <li key={accessKey}>
                                              <Form.Item
                                                {...accessRestField}
                                                name={[accessName, "value"]}
                                                valuePropName="checked"
                                                noStyle
                                              >
                                                <Checkbox>
                                                  {form.getFieldValue([
                                                    "forms",
                                                    name,
                                                    "access",
                                                    accessName,
                                                    "label",
                                                  ])}
                                                </Checkbox>
                                              </Form.Item>
                                            </li>
                                          )
                                        )}
                                      </ul>
                                    )}
                                  </Form.List>
                                </Panel>
                              ))}
                            </Collapse>
                          )}
                        </Form.List>
                      </Col>
                    </Row>
                  )}

                  <Row justify="center" align="middle">
                    <Col span={18} offset={6}>
                      <Form.Item
                        id="informUser"
                        label=""
                        valuePropName="checked"
                        name="inform_user"
                        rules={[{ required: false }]}
                      >
                        <Checkbox
                          disabled={
                            !id
                              ? true
                              : authUser?.email === form.getFieldValue("email")
                              ? true
                              : false
                          }
                        >
                          {text.informUser}
                        </Checkbox>
                      </Form.Item>
                    </Col>
                  </Row>
                  <Row justify="center" align="middle">
                    <Col span={18} offset={6}>
                      <Button
                        type="primary"
                        htmlType="submit"
                        shape="round"
                        loading={submitting}
                      >
                        {id ? text.updateUser : text.addUser}
                      </Button>
                    </Col>
                  </Row>
                </>
              )}
            </Form>
          </Spin>
        </div>
      </div>

      {/* Notification modal */}
      <Modal
        open={isModalVisible}
        onCancel={onCloseModal}
        centered
        width="575px"
        footer={
          <Row justify="center" align="middle">
            <Col>
              <Button className="light" onClick={onCloseModal}>
                {text.cancelButton}
              </Button>
            </Col>
          </Row>
        }
        bodystyle={{ textAlign: "center" }}
      >
        <img src="/assets/user.svg" height="80" />
        <br />
        <br />
        <p>{text.existingApproverTitle}</p>
        <Table
          columns={[
            {
              title: text.formColumn,
              dataIndex: "form",
            },
            {
              title: text.administrationLabel,
              dataIndex: "administration",
            },
          ]}
          dataSource={modalContent}
          rowKey="id"
          pagination={false}
        />
        <br />
        <p>{text.existingApproverDescription}</p>
      </Modal>
    </div>
  );
};

export default AddUser;
