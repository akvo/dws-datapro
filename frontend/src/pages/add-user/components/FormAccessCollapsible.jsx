import React from "react";
import { Collapse, Form, Input, Space, Checkbox } from "antd";
import { config, FORM_READER_ACCESS } from "../../../lib";

const { Panel } = Collapse;

const FormAccessCollapsible = ({ form, formInstance, fields }) => {
  const indexOfReadOnly = config.accessFormTypes.findIndex(
    (af) => af.id === FORM_READER_ACCESS
  );

  const onChange = (checked, name, accessKey) => {
    const forms = formInstance.getFieldValue(["forms"]).map((f, fx) => {
      if (fx === name) {
        return {
          ...f,
          access: config.accessFormTypes.map((af, index) => ({
            ...af,
            value:
              index === accessKey
                ? checked
                : formInstance.getFieldValue([
                    "forms",
                    name,
                    "access",
                    indexOfReadOnly,
                    "value",
                  ])
                ? false
                : f?.access?.[index]?.value,
          })),
        };
      }
      return f;
    });
    formInstance.setFieldsValue({
      forms,
    });
  };

  return (
    <Collapse defaultActiveKey={["0"]}>
      {fields.map(({ key, name, ...restField }) => (
        <Panel
          key={key}
          header={form.getFieldValue(["forms", name, "name"])}
          extra={
            <Space className="extra-access-label">
              {formInstance
                .getFieldValue(["forms", name, "access"])
                .filter((a) => a?.value)
                .map((a) => (
                  <span key={a.id} className="access-label">
                    {a.label}
                  </span>
                ))}
            </Space>
          }
        >
          <Form.Item {...restField} name={[name, "id"]} hidden>
            <Input />
          </Form.Item>
          <Form.List name={[name, "access"]}>
            {(accessFields) => {
              const isReadOnly = formInstance.getFieldValue([
                "forms",
                name,
                "access",
                indexOfReadOnly,
                "value",
              ]);
              return (
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
                          <Checkbox
                            disabled={
                              accessKey !== indexOfReadOnly && isReadOnly
                            }
                            onChange={(e) => {
                              onChange(e.target.checked, name, accessKey);
                            }}
                          >
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
              );
            }}
          </Form.List>
        </Panel>
      ))}
    </Collapse>
  );
};

export default FormAccessCollapsible;
