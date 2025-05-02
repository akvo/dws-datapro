import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { Button, Text } from '@rneui/themed';
import * as DocumentPicker from 'expo-document-picker';
import Icon from 'react-native-vector-icons/Ionicons';
import { FieldLabel } from '../support';
import { FormState } from '../../store';
import { i18n } from '../../lib';
import MIME_TYPES from '../../lib/mime_types';

const TypeAttachment = ({
  onChange,
  keyform,
  id,
  value,
  label,
  required,
  requiredSign = '*',
  tooltip = null,
  rule = null,
}) => {
  const [selectedFile, setSelectedFile] = useState({ name: value });
  const activeLang = FormState.useState((s) => s.lang);
  const trans = i18n.text(activeLang);
  const { allowed_file_types: allowedFileRules } = rule || {};
  const allowedFileTypes = allowedFileRules?.length
    ? allowedFileRules.map((type) => MIME_TYPES?.[type] || 'application/octet-stream')
    : '*/*';

  const onButtonPress = async () => {
    try {
      const { assets, canceled } = await DocumentPicker.getDocumentAsync({
        multiple: false,
        type: allowedFileTypes,
        copyToCacheDirectory: true,
      });
      if (!canceled && assets && assets.length > 0) {
        const result = assets[0];
        onChange(id, result?.uri);
        setSelectedFile(result);
      }
    } catch (error) {
      // Handle any errors that occur during document picking
      // by showing an alert instead of console.log
      Alert.alert('Error', 'An error occurred while picking the document. Please try again.');
    }
  };

  const onRemovePress = () => {
    setSelectedFile(null);
    onChange(id, null);
  };

  return (
    <View style={styles.container}>
      <FieldLabel
        keyform={keyform}
        name={label}
        required={required}
        requiredSign={requiredSign}
        tooltip={tooltip}
      />
      {selectedFile?.name ? (
        <View style={{ marginBottom: 10 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Icon name="document-text" size={20} color="black" style={styles.Icon} />
            <Text style={styles.fileName}>
              {selectedFile?.name?.includes('/')
                ? selectedFile.name.split('/')?.pop()
                : selectedFile?.name}
            </Text>
          </View>
          <Button
            icon={<Icon name="trash" size={20} color="white" style={styles.Icon} />}
            title={trans.buttonRemove}
            onPress={onRemovePress}
            testID="remove-file-button"
            accessibilityLabel="remove-file-button"
            disabled={!selectedFile}
            buttonStyle={styles.removeButton}
          />
        </View>
      ) : (
        <Button
          icon={<Icon name="attach" size={20} color="white" style={styles.Icon} />}
          title={trans.attachButton}
          onPress={onButtonPress}
          testID="attach-file-button"
          accessibilityLabel="attach-file-button"
          buttonStyle={styles.attachButton}
        />
      )}
    </View>
  );
};

export default TypeAttachment;

const styles = StyleSheet.create({
  container: {
    flexDirection: 'column',
    marginBottom: 10,
  },
  removeButton: {
    backgroundColor: '#ec003f',
    marginTop: 10,
  },
  attachButton: {
    backgroundColor: '#1E90FF',
  },
  fileName: {
    marginBottom: 10,
  },
  Icon: {
    marginRight: 10,
  },
});
