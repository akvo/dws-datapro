import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Image } from 'react-native';
import { Text, Button, Input } from '@rneui/themed';
import { useSQLiteContext } from 'expo-sqlite';
import { CenterLayout } from '../components';
import { BuildParamsState, UIState } from '../store';
import { api, i18n } from '../lib';
import { crudConfig } from '../database/crud';
import appIcon from '../assets/icon.png';

const GetStarted = ({ navigation }) => {
  // eslint-disable-next-line global-require
  const [currentConfig, setCurrentConfig] = useState({});
  const [IPAddr, setIPAddr] = useState(null);
  const serverURLState = BuildParamsState.useState((s) => s.serverURL);
  const authenticationType = BuildParamsState.useState((s) => s.authenticationType);
  const activeLang = UIState.useState((s) => s.lang);
  const trans = i18n.text(activeLang);
  const db = useSQLiteContext();

  const getConfig = useCallback(async () => {
    const config = await crudConfig.getConfig(db);
    if (config) {
      setCurrentConfig(config);
    }
  }, [db]);

  const isServerURLDefined = useMemo(
    () => currentConfig?.serverURL || serverURLState,
    [currentConfig?.serverURL, serverURLState],
  );

  useEffect(() => {
    getConfig();
  }, [getConfig]);

  const goToLogin = async () => {
    if (IPAddr) {
      BuildParamsState.update((s) => {
        s.serverURL = IPAddr;
      });
      api.setServerURL(IPAddr);
      // save server URL
      await crudConfig.updateConfig(db, { serverURL: IPAddr });
    }
    setTimeout(() => {
      if (authenticationType.includes('code_assignment')) {
        navigation.navigate('AuthForm');
        return;
      }
      navigation.navigate('AuthByPassForm');
    }, 100);
  };

  const titles = [trans.getStartedTitle1, trans.getStartedTitle2, trans.getStartedTitle3];
  return (
    <CenterLayout title={titles}>
      <Image source={appIcon} style={{ width: 110, height:110, borderRadius: 4 }} />
      <CenterLayout.Titles items={titles} />
      <Text>{trans.getStartedSubTitle}</Text>
      {!isServerURLDefined && (
        <Input
          placeholder={trans.getStartedInputServer}
          onChangeText={setIPAddr}
          testID="server-url-field"
        />
      )}
      <Button title="primary" onPress={goToLogin} testID="get-started-button">
        {trans.buttonGetStarted}
      </Button>
    </CenterLayout>
  );
};

export default GetStarted;
