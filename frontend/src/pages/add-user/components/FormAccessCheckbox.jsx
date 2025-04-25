import React from "react";
import { Form, Checkbox, List, Input } from "antd";

const FormAccessCheckbox = ({ form, fields }) => {
  return (
    <List
      itemLayout="horizontal"
      dataSource={fields}
      renderItem={({ key, name, ...restField }) => (
        <List.Item key={key}>
          <Form.Item {...restField} name={[name, "id"]} hidden>
            <Input />
          </Form.Item>
          <Form.Item
            {...restField}
            name={[name, "checked"]}
            valuePropName="checked"
            noStyle
          >
            <Checkbox>{form.getFieldValue(["forms", name, "name"])}</Checkbox>
          </Form.Item>
        </List.Item>
      )}
    />
  );
};

export default FormAccessCheckbox;
