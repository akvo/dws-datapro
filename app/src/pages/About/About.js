import React, { useState, useCallback } from 'react';
import { View, Linking, Alert, StyleSheet, Text } from 'react-native';
import { Icon, Dialog, Button } from '@rneui/themed';
import * as Sentry from '@sentry/react-native';
import { BaseLayout } from '../../components';
import { BuildParamsState, UIState } from '../../store';
import { i18n, api } from '../../lib';

const AboutHome = () => {
  const { appVersion, apkURL, apkName } = BuildParamsState.useState((s) => s);
  const { lang } = UIState.useState((s) => s);
  const trans = i18n.text(lang);
  const [visible, setVisible] = useState(false);
  const [checking, setChecking] = useState(false);
  const [updateInfo, setUpdateInfo] = useState({ status: null, text: '' });

  const handleCheckAppVersion = () => {
    setChecking(true);
    setVisible(true);
    api
      .get(`/apk/version/${appVersion}`)
      .then((res) => {
        // update
        setUpdateInfo({
          status: 200,
          text: `${trans.newVersionAvailable} (v ${res.data.version})`,
        });
      })
      .catch((e) => {
        // no update
        Sentry.captureMessage('[About] Unable to fetch app version');
        Sentry.captureException(e);
        setUpdateInfo({ status: e?.response?.status || 500, text: trans.noUpdateFound });
      })
      .finally(() => {
        setChecking(false);
      });
  };

  const handleUpdateButton = useCallback(async () => {
    // if the link is supported for links with custom URL scheme.
    const supported = await Linking.canOpenURL(apkURL);
    if (supported) {
      // Opening the link with some app, if the URL scheme is "http" the web link should be opened
      // by some browser in the mobile
      await Linking.openURL(apkURL);
    } else {
      Alert.alert(`Don't know how to open this URL: ${apkURL}`);
    }
  }, [apkURL]);

  return (
    <BaseLayout title={trans.about} rightComponent={false}>
      <BaseLayout.Content>
        <View>
          {/* About App Info */}
          <View style={styles.listItem}>
            <View style={styles.listItemContent}>
              <Text style={styles.listItemTitle}>{`${trans.about} ${apkName}`}</Text>
              <Text style={styles.listItemSubtitle}>{trans.aboutAppDescription}</Text>
            </View>
          </View>

          {/* App Version */}
          <View style={styles.listItem}>
            <View style={styles.listItemContent}>
              <Text style={styles.listItemTitle}>{trans.appVersionLabel}</Text>
              <Text style={styles.listItemSubtitle}>{appVersion}</Text>
            </View>
          </View>

          {/* Update button */}
          <Button
            title={trans.updateApp}
            onPress={handleCheckAppVersion}
            icon={<Icon name="system-update" type="materialicon" color="#fff" />}
            buttonStyle={styles.updateButton}
            titleStyle={styles.updateButtonText}
            testID="update-button"
          />
          {/* EOL Update button */}

          <Dialog isVisible={visible}>
            {checking ? (
              <View>
                <Dialog.Loading />
                <Text style={{ textAlign: 'center' }}>{trans.checkingVersion}</Text>
              </View>
            ) : (
              <View>
                <Text>{updateInfo.text}</Text>
                <Dialog.Actions>
                  {updateInfo.status === 200 ? (
                    <Dialog.Button onPress={handleUpdateButton}>{trans.buttonUpdate}</Dialog.Button>
                  ) : (
                    ''
                  )}
                  <Dialog.Button onPress={() => setVisible(false)}>
                    {trans.buttonCancel}
                  </Dialog.Button>
                </Dialog.Actions>
              </View>
            )}
          </Dialog>
        </View>
      </BaseLayout.Content>
    </BaseLayout>
  );
};

const styles = StyleSheet.create({
  listItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  listItemContent: {
    flexDirection: 'column',
  },
  listItemTitle: {
    fontWeight: 'bold',
  },
  listItemSubtitle: {
    color: '#666',
    paddingTop: 14,
  },
  updateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007bff',
    borderRadius: 5,
    marginVertical: 16,
    marginHorizontal: 10,
  },
  updateButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    marginRight: 10,
  },
});

export default AboutHome;
