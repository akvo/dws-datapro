import React from "react";
import { Form, Space, Select, Button, Row, Col } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { AdministrationDropdown } from "../../../components";

const FormRoles = ({ form, text, roles = [] }) => {
  return (
    <Form.List
      name="roles"
      hasFeedback
      rules={[
        () => ({
          validator(_, value) {
            if (value?.length > 0) {
              return Promise.resolve();
            }
            return Promise.reject(new Error(text.rolesRequired));
          },
        }),
      ]}
    >
      {(fields, { add, remove }) => (
        <>
          {fields.map((field) => {
            const maxLevel = roles?.find(
              (r) =>
                r.value === form.getFieldValue(["roles", field.name, "role"])
            )?.administration_level;

            return (
              <Row key={field.key} gutter={8}>
                <Col>
                  <Space align="baseline">
                    <Form.Item
                      noStyle
                      shouldUpdate={(prevValues, currentValues) =>
                        prevValues.roles?.[field.name]?.role !==
                        currentValues.roles?.[field.name]?.role
                      }
                    >
                      {() => (
                        <Form.Item
                          {...field}
                          name={[field.name, "role"]}
                          rules={[
                            {
                              required: true,
                            },
                          ]}
                        >
                          <Select
                            showSearch
                            placeholder={text.selectRole}
                            options={roles.filter(
                              (role) =>
                                !fields.some(
                                  (f) =>
                                    f.name !== field.name &&
                                    form.getFieldValue([
                                      "roles",
                                      f.name,
                                      "role",
                                    ]) === role.value
                                )
                            )}
                            optionFilterProp="label"
                            filterOption={(input, option) =>
                              option.label
                                .toLowerCase()
                                .includes(input.toLowerCase())
                            }
                            style={{ minWidth: 240, width: "100%" }}
                          />
                        </Form.Item>
                      )}
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, "administration"]}>
                      <AdministrationDropdown
                        withLabel={false}
                        persist={true}
                        size="large"
                        width="100%"
                        maxLevel={maxLevel}
                        selectedAdministrations={form.getFieldValue([
                          "roles",
                          field.name,
                          "administration",
                        ])}
                      />
                    </Form.Item>
                    <MinusCircleOutlined onClick={() => remove(field.name)} />
                  </Space>
                </Col>
              </Row>
            );
          })}

          <Form.Item>
            <Button
              type="dashed"
              onClick={() => add()}
              block
              icon={<PlusOutlined />}
            >
              {text.addRole}
            </Button>
          </Form.Item>
        </>
      )}
    </Form.List>
  );
};

export default FormRoles;
