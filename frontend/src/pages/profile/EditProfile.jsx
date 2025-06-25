import React, { useMemo, useState, useEffect } from "react";
import "./style.scss";
import {
  Space,
  Card,
  Divider,
  Row,
  Col,
  Tag,
  Button,
  Form,
  Input,
  Select,
} from "antd";
import { api, store, uiText } from "../../lib";
import { Breadcrumbs, DescriptionPanel } from "../../components";
import { ProfileTour } from "./components";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../../util/hooks";
import { first, last } from "lodash";

const { Option } = Select;

const EditProfile = () => {
  const [submitting, setSubmitting] = useState(false);
  const [organisations, setOrganisations] = useState([]);
  const { user: authUser, language } = store.useState((s) => s);
  const { trained } = authUser;

  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { notify } = useNotification();

  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const descriptionData = text.profileDes;
  const [firstName, lastName] = useMemo(() => {
    const names = authUser?.name?.split(/\s+/);
    return [first(names), last(names)];
  }, [authUser]);

  const trainedBadge = useMemo(() => {
    if (trained) {
      return <Tag color="warning">Trained</Tag>;
    }
  }, [trained]);

  const pagePath = [
    {
      title: text.controlCenter,
      link: "/control-center",
    },
    {
      title:
        (
          <Space align="center" size={15}>
            {authUser?.name}
            {trainedBadge}
          </Space>
        ) || text.profileLabel,
    },
  ];

  const onFinish = (values) => {
    setSubmitting(true);
    api
      .put("/update-profile", values)
      .then((res) => {
        notify({
          type: "success",
          message: "Profile updated successfully ",
        });
        setSubmitting(false);

        store.update((s) => {
          s.user = res.data;
        });
        form.resetFields();
        // Redirect to profile page after successful update
        navigate("/control-center/profile");
      })
      .catch((err) => {
        notify({
          type: "error",
          message:
            err?.response?.data?.detail ||
            "An error occurred while updating the profile.",
        });
        setSubmitting(false);
      });
  };

  useEffect(() => {
    if (!organisations.length) {
      // filter by 1 for member attribute
      api.get("organisations?filter=1").then((res) => {
        setOrganisations(res.data);
      });
    }
  }, [organisations]);

  return (
    <div id="profile">
      <Row justify="space-between">
        <Breadcrumbs pagePath={pagePath} />
        <ProfileTour />
      </Row>
      <DescriptionPanel
        description={descriptionData}
        title={text.profileLabel}
      />
      <Divider />
      <Card style={{ padding: 0, marginBottom: 12 }}>
        <Form
          name="adm-form"
          form={form}
          labelCol={{ span: 6 }}
          wrapperCol={{ span: 18 }}
          initialValues={{
            ...authUser,
            first_name: firstName,
            last_name: lastName,
            organisation: authUser?.organisation?.id || null,
          }}
          onFinish={onFinish}
        >
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
              rules={[{ required: true, message: text.valOrganization }]}
            >
              <Select
                getPopupContainer={(trigger) => trigger.parentNode}
                placeholder={text.selectOne}
                allowClear
                showSearch
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
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

          <Row justify="center" align="middle">
            <Col span={18} offset={6}>
              <Button
                type="primary"
                htmlType="submit"
                shape="round"
                loading={submitting}
              >
                {text.saveButton}
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>
    </div>
  );
};

export default React.memo(EditProfile);
