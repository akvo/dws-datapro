import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { View, FlatList, StyleSheet, Text, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';
import * as SQLite from 'expo-sqlite';
import moment from 'moment';
import { FormState, UIState, UserState } from '../store';
import { i18n } from '../lib';
import { BaseLayout, FAButton } from '../components';
import { getCurrentTimestamp } from '../form/lib';
import { crudDataPoints } from '../database/crud';

const Submission = ({ navigation, route }) => {
  const [search, setSearch] = useState('');
  const [data, setData] = useState([]);

  const activeForm = FormState.useState((s) => s.form);
  const activeLang = UIState.useState((s) => s.lang);
  const { id: activeUserId } = UserState.useState((s) => s);
  const trans = i18n.text(activeLang);
  const db = SQLite.useSQLiteContext();

  const datapoints = useMemo(
    () =>
      data.filter(
        (d) => (search && d?.name?.toLowerCase().includes(search.toLowerCase())) || !search,
      ),
    [data, search],
  );

  const goToNewForm = useCallback(() => {
    FormState.update((s) => {
      s.surveyStart = getCurrentTimestamp();
      s.prevAdmAnswer = null;
    });
    navigation.navigate('FormPage', {
      ...route?.params,
      newSubmission: true,
    });
  }, [navigation, route]);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      key={item.id}
      onPress={() =>
        navigation.navigate('FormOptions', {
          id: item.id,
          name: item.name,
          uuid: item.uuid,
          formId: activeForm.formId,
        })
      }
      testID={`submission-item-${item.id}`}
      style={styles.itemContainer}
      activeOpacity={0.6}
    >
      <View style={styles.iconContainer}>
        <Icon
          name={item.isSynced ? 'checkmark' : 'time'}
          size={24}
          color={item.isSynced ? '#4CAF50' : '#FFA000'}
        />
      </View>
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle}>{item.name}</Text>
        <Text style={styles.itemAdministration}>Administration: {item.administration}</Text>
        <Text style={styles.itemDate}>
          {trans.createdLabel} {item.createdAt}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const fetchData = useCallback(async () => {
    let rows = await crudDataPoints.selectDataPointsByFormAndSubmitted(db, {
      form: activeForm.id,
      submitted: 1,
      user: activeUserId,
    });
    rows = rows.map((res) => {
      const createdAt = moment(res.createdAt).format('DD/MM/YYYY hh:mm A');
      const syncedAt = res.syncedAt ? moment(res.syncedAt).format('DD/MM/YYYY hh:mm A') : '-';
      return {
        ...res,
        createdAt,
        syncedAt,
        isSynced: !!res.syncedAt,
      };
    });
    setData(rows);
  }, [activeForm.id, activeUserId, db]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <BaseLayout
      title={route?.params?.name}
      subTitle={route?.params?.subTitle}
      search={{
        show: true,
        value: search,
        action: setSearch,
      }}
      rightComponent={false}
    >
      <BaseLayout.Content>
        <View style={styles.container}>
          <FlatList
            data={datapoints}
            renderItem={renderItem}
            keyExtractor={(item) => item.id}
            testID="submission-list"
            contentContainerStyle={styles.flatListContent}
          />
        </View>
      </BaseLayout.Content>
      <FAButton
        label={trans.newSubmissionText}
        onPress={goToNewForm}
        testID="new-submission-button"
        icon={{ name: 'add-circle', size: 20, color: 'white' }}
      />
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
    padding: 12,
    backgroundColor: 'white',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 2,
  },
  iconContainer: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    marginRight: 12,
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
  itemAdministration: {
    fontSize: 14,
    color: '#757575',
    marginBottom: 2,
  },
  itemDate: {
    fontSize: 12,
    color: '#9e9e9e',
  },
});

export default Submission;
