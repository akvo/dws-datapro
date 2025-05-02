import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { ListItem, Image, Button } from '@rneui/themed';
import moment from 'moment';
import * as Linking from 'expo-linking';
import { FormState, UIState } from '../../store';
import { cascades, i18n } from '../../lib';
import { BaseLayout } from '../../components';
import FormDataNavigation from './FormDataNavigation';
import { QUESTION_TYPES } from '../../lib/constants';

const SubtitleContent = ({ index, answers, type, id, source = null, option = [] }) => {
  const activeLang = UIState.useState((s) => s.lang);
  const trans = i18n.text(activeLang);
  const [cascadeValue, setCascadeValue] = useState(null);

  const openFileManager = async (uri) => {
    const supported = await Linking.canOpenURL(uri);
    if (supported) {
      await Linking.openURL(uri);
    } else {
      Alert.alert("Don't know how to open this URL:", uri);
    }
  };

  const fetchCascade = useCallback(async () => {
    if (source) {
      const cascadeID = parseInt(answers?.[id], 10);
      const csValue = await cascades.loadDataSource(source, cascadeID);
      setCascadeValue(csValue);
    }
  }, [answers, id, source]);

  useEffect(() => {
    fetchCascade();
  }, [fetchCascade]);

  switch (type) {
    case QUESTION_TYPES.geo:
      return (
        <View testID={`text-type-geo-${index}`}>
          <Text>
            {trans.latitude}: {answers?.[id]?.[0]}
          </Text>
          <Text>
            {trans.longitude}: {answers?.[id]?.[1]}
          </Text>
        </View>
      );
    case QUESTION_TYPES.cascade:
      return <Text testID={`text-answer-${index}`}>{cascadeValue ? cascadeValue.name : '-'}</Text>;
    case QUESTION_TYPES.date:
      return (
        <Text testID={`text-answer-${index}`}>
          {answers?.[id] ? moment(answers[id]).format('YYYY-MM-DD') : '-'}
        </Text>
      );
    case QUESTION_TYPES.option:
    case QUESTION_TYPES.multiple_option:
      return answers?.[id]
        ?.map((a) => {
          const findOption = option?.find((o) => o?.value === a);
          return findOption?.label;
        })
        ?.join(', ');
    case QUESTION_TYPES.attachment:
      return (
        <View testID={`text-type-attachment-${index}`} style={{ width: '100%' }}>
          <Text
            testID={`text-answer-${index}`}
            style={{ color: 'blue', textDecorationLine: 'underline' }}
          >
            {answers?.[id] ? answers[id].split('/').pop() : '-'}
          </Text>
          <Button
            title={trans.openFileButton}
            onPress={() => openFileManager(answers?.[id])}
            testID={`open-file-button-${index}`}
            buttonStyle={{ backgroundColor: '#1E90FF', marginTop: 8 }}
          />
        </View>
      );
    default:
      return (
        <Text testID={`text-answer-${index}`}>
          {answers?.[id] || answers?.[id] === 0 ? answers[id] : '-'}
        </Text>
      );
  }
};

const FormDataDetails = ({ navigation, route }) => {
  const selectedForm = FormState.useState((s) => s.form);
  const currentValues = FormState.useState((s) => s.currentValues);
  const [currentPage, setCurrentPage] = useState(0);

  const { json: formJSON } = selectedForm || {};

  const form = formJSON ? JSON.parse(formJSON) : {};
  const currentGroup = form?.question_group?.[currentPage] || [];
  const totalPage = form?.question_group?.length || 0;
  const questions = currentGroup?.question || [];

  useEffect(
    () =>
      navigation.addListener('beforeRemove', (e) => {
        // Prevent default behavior of leaving the screen
        e.preventDefault();

        if (Object.keys(currentValues).length) {
          FormState.update((s) => {
            s.currentValues = {};
          });
          navigation.dispatch(e.data.action);
        }
      }),
    [navigation, currentValues],
  );

  return (
    <BaseLayout title={route?.params?.name} rightComponent={false}>
      <ScrollView>
        {questions?.map((q, i) =>
          q.type === QUESTION_TYPES.photo && currentValues?.[q.id] ? (
            <View key={q.id} style={styles.containerImage}>
              <Text style={styles.title} testID={`text-question-${i}`}>
                {q.label}
              </Text>
              <Image
                source={{ uri: currentValues?.[q.id] }}
                testID={`image-answer-${i}`}
                style={{ width: '100%', height: 200, aspectRatio: 1 }}
              />
            </View>
          ) : (
            <ListItem key={q.id} bottomDivider>
              <ListItem.Content>
                <ListItem.Title style={styles.title} testID={`text-question-${i}`}>
                  {q.label}
                </ListItem.Title>
                <ListItem.Subtitle>
                  <SubtitleContent
                    index={i}
                    answers={currentValues}
                    type={q.type}
                    id={q.id}
                    source={q?.source}
                    option={q?.option}
                  />
                </ListItem.Subtitle>
              </ListItem.Content>
            </ListItem>
          ),
        )}
      </ScrollView>
      <FormDataNavigation
        totalPage={totalPage}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
      />
    </BaseLayout>
  );
};

const styles = StyleSheet.create({
  title: {
    fontWeight: '700',
    fontSize: 14,
    marginBottom: 4,
  },
  containerImage: {
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    padding: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderTopColor: 'transparent',
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderBottomColor: 'silver',
  },
});

export default FormDataDetails;
