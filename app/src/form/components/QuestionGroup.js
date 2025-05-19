/* eslint-disable react/jsx-props-no-spreading */
import React, { useRef, useEffect } from 'react';
import { View, SectionList, FlatList } from 'react-native';

import QuestionField from './QuestionField';
import { FieldGroupHeader, RepeatSection } from '../support';
import { FormState } from '../../store';
import styles from '../styles';

const QuestionGroup = ({ index, group, activeQuestions, dependantQuestions = [] }) => {
  const values = FormState.useState((s) => s.currentValues);
  const listRef = useRef(null);

  // For non-repeatable groups, get questions that belong to this group
  const questions = !group?.repeatable
    ? activeQuestions.filter((q) => q.group_id === group.id || q.group_name === group.name)
    : [];

  // Handle onChange for all questions
  const handleOnChange = (id, value) => {
    // Handle dependencies with dependantQuestions
    FormState.update((s) => {
      s.currentValues = { ...s.currentValues, [id]: value };
    });
  };

  useEffect(() => {
    if (listRef.current) {
      if (group?.repeatable) {
        listRef.current.scrollToLocation({
          animated: true,
          sectionIndex: 0,
          itemIndex: 0,
        });
      } else {
        listRef.current.scrollToOffset({ animated: true, offset: 0 });
      }
    }
  }, [index, group?.repeatable]);

  // Render header for repeatable groups in SectionList
  const renderSectionHeader = ({ section }) => {
    if (section.repeatIndex !== 0) {
      return <RepeatSection group={group} repeatIndex={section.repeatIndex} />;
    }
    return null;
  };

  // If group is repeatable, use SectionList with sections directly from the group object
  if (group?.repeatable && group.sections) {
    return (
      <View style={{ paddingBottom: 48 }}>
        <FieldGroupHeader index={index} {...group} />

        <SectionList
          ref={listRef}
          sections={group.sections}
          keyExtractor={(item, itemIndex) => `question-${item.id}-${itemIndex}`}
          renderItem={({ item }) => {
            const fieldValue = values?.[item.id];

            return (
              <View key={`question-${item.id}`} style={styles.questionContainer}>
                <QuestionField
                  keyform={item.id}
                  field={item}
                  onChange={handleOnChange}
                  value={fieldValue}
                  questions={activeQuestions}
                />
              </View>
            );
          }}
          renderSectionHeader={renderSectionHeader}
          stickySectionHeadersEnabled={false}
          extraData={[group, values, activeQuestions, dependantQuestions]}
          removeClippedSubviews={false}
        />
      </View>
    );
  }

  // For non-repeatable groups, use FlatList
  return (
    <View style={{ paddingBottom: 48 }}>
      <FieldGroupHeader index={index} {...group} />

      <FlatList
        ref={listRef}
        scrollEnabled
        data={questions}
        keyExtractor={(item) => `question-${item.id}`}
        renderItem={({ item: field }) => {
          const fieldValue = values?.[field.id];

          return (
            <View key={`question-${field.id}`} style={styles.questionContainer}>
              <QuestionField
                keyform={field.id}
                field={field}
                onChange={handleOnChange}
                value={fieldValue}
                questions={questions}
              />
            </View>
          );
        }}
        extraData={[group, values, activeQuestions, dependantQuestions]}
        removeClippedSubviews={false}
      />
    </View>
  );
};

export default QuestionGroup;
