import React from 'react';
import { View } from 'react-native';
import { Input } from '@rneui/themed';
import { FieldLabel } from '../support';
import styles from '../styles';

const TypeText = ({
  onChange,
  value,
  keyform,
  id,
  label,
  tooltip,
  required,
  requiredSign = '*',
  meta_uuid: metaUUID,
  disabled,
}) => {
  const requiredValue = required ? requiredSign : null;
  const inputContainerStyle =
    metaUUID || disabled
      ? { ...styles.inputFieldContainer, ...styles.inputFieldDisabled }
      : styles.inputFieldContainer;
  return (
    <View>
      <FieldLabel keyform={keyform} name={label} tooltip={tooltip} requiredSign={requiredValue} />
      <Input
        inputContainerStyle={inputContainerStyle}
        multiline
        numberOfLines={1}
        onChangeText={(val) => {
          if (onChange) {
            onChange(id, val);
          }
        }}
        value={value}
        testID="type-text"
        disabled={metaUUID || disabled}
      />
    </View>
  );
};

export default TypeText;
