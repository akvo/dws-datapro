import React, { useState, useMemo } from 'react';
import { View } from 'react-native';
import { ListItem, Switch } from '@rneui/themed';
import * as Crypto from 'expo-crypto';
import * as Sentry from '@sentry/react-native';
import * as SQLite from 'expo-sqlite';
import { BaseLayout } from '../../components';
import { config } from './config';
import { BuildParamsState, UIState, AuthState, UserState } from '../../store';
import DialogForm from './DialogForm';
import { backgroundTask, i18n } from '../../lib';
import { accuracyLevels } from '../../lib/loc';
import { crudConfig } from '../../database/crud';
import { DATABASE_NAME } from '../../lib/constants';

const SettingsForm = ({ route }) => {
  const [edit, setEdit] = useState(null);
  const [showDialog, setShowDialog] = useState(false);

  const { serverURL, dataSyncInterval, gpsThreshold, gpsAccuracyLevel, geoLocationTimeout } =
    BuildParamsState.useState((s) => s);
  const { password, authenticationCode, useAuthenticationCode } = AuthState.useState((s) => s);
  const { lang, isDarkMode, fontSize } = UIState.useState((s) => s);
  const { name, syncWifiOnly } = UserState.useState((s) => s);
  const store = useMemo(
    () => ({
      AuthState,
      BuildParamsState,
      UIState,
      UserState,
    }),
    [],
  );
  const [settingsState, setSettingsState] = useState({
    serverURL,
    name,
    password,
    authenticationCode,
    useAuthenticationCode,
    lang,
    isDarkMode,
    fontSize,
    dataSyncInterval,
    syncWifiOnly,
    gpsThreshold,
    gpsAccuracyLevel,
    geoLocationTimeout,
  });

  const nonEnglish = lang !== 'en';
  const curConfig = config.find((c) => c.id === route?.params?.id);
  const pageTitle = nonEnglish ? i18n.transform(lang, curConfig)?.name : route?.params?.name;

  const editState = useMemo(() => {
    if (edit && edit?.key) {
      const [stateName, stateKey] = edit?.key?.split('.') || [];
      return [store[stateName], stateKey];
    }
    return null;
  }, [edit, store]);

  const handleEditPress = (id) => {
    const findEdit = list.find((item) => item.id === id);
    if (findEdit) {
      setEdit({
        ...findEdit,
        value: settingsState[findEdit?.name] || null,
      });
      setShowDialog(true);
    }
  };

  const handleUpdateOnDB = async (field, value) => {
    const dbUpdate = await SQLite.openDatabaseAsync(DATABASE_NAME, {
      useNewConnection: true,
    });
    const configFields = [
      'apVersion',
      'authenticationCode',
      'serverURL',
      'syncInterval',
      'syncWifiOnly',
      'lang',
      'gpsThreshold',
      'gpsAccuracyLevel',
      'geoLocationTimeout',
    ];
    if (configFields.includes(field)) {
      await crudConfig.updateConfig(dbUpdate, { [field]: value });
    }
    if (field === 'name') {
      await crudConfig.updateConfig(dbUpdate, { name: value });
    }
    if (field === 'password') {
      const encrypted = await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA1, value);
      await crudConfig.updateConfig(dbUpdate, { password: encrypted });
    }
    await dbUpdate.closeAsync();
  };

  const handleOnRestarTask = async (v) => {
    try {
      await backgroundTask.unregisterBackgroundTask('sync-form-submission');
      await backgroundTask.registerBackgroundTask('sync-form-submission', parseInt(v, 10));
    } catch (error) {
      Sentry.captureMessage('[SettingsForm] handleOnRestarTask failed');
      Sentry.captureException(error);
      Promise.reject(error);
    }
  };

  const handleOKPress = async (inputValue) => {
    setShowDialog(false);
    if (edit && inputValue) {
      const [stateData, stateKey] = editState;
      stateData.update((d) => {
        d[stateKey] = inputValue;
      });
      setSettingsState({
        ...settingsState,
        [stateKey]: inputValue,
      });
      if (stateKey === 'dataSyncInterval') {
        await handleUpdateOnDB('syncInterval', inputValue);
        await handleOnRestarTask(inputValue);
      } else {
        await handleUpdateOnDB(stateKey, inputValue);
      }
      setEdit(null);
    }
  };
  const handleCancelPress = () => {
    setShowDialog(false);
    setEdit(null);
  };

  const handleOnSwitch = (value, key) => {
    const [stateName, stateKey] = key.split('.');
    const tinyIntVal = value ? 1 : 0;
    store[stateName].update((s) => {
      s[stateKey] = tinyIntVal;
    });
    setSettingsState({
      ...settingsState,
      [stateKey]: tinyIntVal,
    });
    handleUpdateOnDB(stateKey, tinyIntVal);
  };

  const renderSubtitle = ({ type: inputType, name: fieldName, description }) => {
    const itemDesc = nonEnglish ? i18n.transform(lang, description)?.name : description?.name;
    if (inputType === 'switch' || inputType === 'password') {
      return itemDesc;
    }
    if (fieldName === 'gpsAccuracyLevel' && settingsState?.[fieldName]) {
      const findLevel = accuracyLevels.find((l) => l.value === settingsState[fieldName]);
      return findLevel?.label || itemDesc;
    }
    return settingsState?.[fieldName];
  };

  const list = useMemo(() => {
    if (route.params?.id) {
      const findConfig = config.find((c) => c?.id === route.params.id);
      return findConfig ? findConfig.fields : [];
    }
    return [];
  }, [route.params?.id]);

  return (
    <BaseLayout title={pageTitle} rightComponent={false}>
      <BaseLayout.Content>
        <View>
          {list.map((l, i) => {
            const itemTitle = nonEnglish ? i18n.transform(lang, l)?.label : l.label;
            return (
              <ListItem
                key={l.id}
                testID={`settings-form-item-${i}`}
                onPress={() => {
                  if (l.editable && l.type !== 'switch') {
                    handleEditPress(l.id);
                  }
                }}
                bottomDivider
              >
                <ListItem.Content>
                  <ListItem.Title>{itemTitle}</ListItem.Title>
                  <ListItem.Subtitle>{renderSubtitle(l)}</ListItem.Subtitle>
                </ListItem.Content>
                {l.type === 'switch' && (
                  <Switch
                    onValueChange={(value) => handleOnSwitch(value, l.key)}
                    value={settingsState?.[l.name] === 1}
                    testID={`settings-form-switch-${i}`}
                  />
                )}
              </ListItem>
            );
          })}
        </View>
        <DialogForm
          onOk={handleOKPress}
          onCancel={handleCancelPress}
          showDialog={showDialog}
          edit={edit}
          initValue={edit?.value}
        />
      </BaseLayout.Content>
    </BaseLayout>
  );
};

export default SettingsForm;
