/* eslint-disable react/jsx-props-no-spreading */
import React from 'react';
import { View } from 'react-native';
import { Input } from '@rneui/themed';
import { FieldLabel } from '../support';
import styles from '../styles';
import { addPreffix, addSuffix } from './TypeInput';

const TypeNumber = ({
  onChange,
  value,
  keyform,
  id,
  label,
  required,
  requiredSign = '*',
  disabled = false,
  addonAfter = null,
  addonBefore = null,
  tooltip = null,
}) => {
  const requiredValue = required ? requiredSign : null;
  return (
    <View>
      <FieldLabel keyform={keyform} name={label} tooltip={tooltip} requiredSign={requiredValue} />
      <Input
        inputContainerStyle={styles.inputFieldContainer}
        keyboardType="numeric"
        onChangeText={(val) => {
          if (onChange) {
            onChange(id, val);
          }
        }}
        value={value}
        testID="type-number"
        {...addPreffix(addonBefore)}
        {...addSuffix(addonAfter)}
        disabled={disabled}
      />
    </View>
  );
};

export default TypeNumber;
