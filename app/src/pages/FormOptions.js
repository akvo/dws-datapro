import React, { useCallback, useEffect, useState } from 'react';
import { View, FlatList, StyleSheet, Text, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import * as SQLite from 'expo-sqlite';
import { FormState, UIState } from '../store';
import { i18n } from '../lib';
import { BaseLayout } from '../components';
import { crudForms } from '../database/crud';

const FormOptions = ({ navigation, route }) => {
  const [forms, setForms] = useState([]);
  const activeForm = FormState.useState((s) => s.form);
  const activeLang = UIState.useState((s) => s.lang);
  const trans = i18n.text(activeLang);
  const db = SQLite.useSQLiteContext();

  const goToSubmission = (selectedForm) => {
    FormState.update((s) => {
      s.form = selectedForm;
    });
    navigation.navigate('Submission', {
      id: selectedForm?.id,
      name: selectedForm.name,
      subTitle: route?.params?.name,
      uuid: route?.params?.uuid,
      formId: selectedForm.formId,
    });
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      key={item.id}
      onPress={() => goToSubmission(item)}
      testID={`form-item-${item.id}`}
      style={styles.itemContainer}
      activeOpacity={0.6}
    >
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle}>{item.name}</Text>
        <Text style={styles.itemVersion}>{`${trans.versionLabel}${item.version}`}</Text>
      </View>
      <Icon name="chevron-right" size={18} color="#ccc" />
    </TouchableOpacity>
  );

  const fetchForms = useCallback(async () => {
    let rows = await crudForms.selectFormByParentId(db, { parentId: activeForm?.formId });
    rows = rows.map((r) => ({ ...r, parentName: activeForm.name, parentDBId: activeForm.id }));
    setForms(rows);
  }, [db, activeForm]);

  useEffect(() => {
    fetchForms();
  }, [fetchForms]);

  return (
    <BaseLayout title={route?.params?.name} rightComponent={false}>
      <BaseLayout.Content>
        <View style={styles.container}>
          <FlatList
            data={forms}
            renderItem={renderItem}
            keyExtractor={(item) => item.id}
            testID="form-list"
            contentContainerStyle={styles.flatListContent}
          />
        </View>
      </BaseLayout.Content>
    </BaseLayout>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
  },
  flatListContent: {
    padding: 8,
  },
  itemContainer: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    marginBottom: 10,
    borderBottomColor: '#E0E0E0',
    borderBottomWidth: 1,
  },
  itemContent: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#212121',
    marginBottom: 4,
  },
  itemVersion: {
    fontSize: 12,
    color: '#9e9e9e',
  },
});

export default FormOptions;
