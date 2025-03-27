/* eslint-disable react/jsx-props-no-spreading */
import React from 'react';
import { View } from 'react-native';

import Question from './Question';
import { FieldGroupHeader } from '../support';

const QuestionGroup = ({ index, group, activeQuestions, dependantQuestions = [] }) => (
  <View style={{ paddingBottom: 48 }}>
    <FieldGroupHeader index={index} {...group} />
    <Question {...{ group, activeQuestions, index, dependantQuestions }} />
  </View>
);

export default QuestionGroup;
