/* eslint-disable react/jsx-props-no-spreading */
import React, { useRef, useEffect, useState } from 'react';
import { View, SectionList, FlatList, Keyboard, Dimensions } from 'react-native';

import QuestionField from './QuestionField';
import { FieldGroupHeader, RepeatSection } from '../support';
import { FormState } from '../../store';
import styles from '../styles';

const QuestionGroup = ({ index, group, activeQuestions, dependantQuestions = [] }) => {
  const values = FormState.useState((s) => s.currentValues);
  const listRef = useRef(null);
  const [selectedInputY, setSelectedInputY] = useState(0);
  const [selectedInputHeight, setSelectedInputHeight] = useState(0);

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

  // Handle focus event for input fields
  const handleInputFocus = (y, height) => {
    setSelectedInputY(y);
    setSelectedInputHeight(height);
  };

  // When the keyboard appears or the input field is focused, adjust scrolling
  useEffect(() => {
    const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', (e) => {
      if (!listRef.current || selectedInputY === 0) return;

      const { height: windowHeight } = Dimensions.get('window');
      const keyboardHeight = e.endCoordinates.height;
      const visibleAreaBottom = windowHeight - keyboardHeight;

      // Calculate if the input is partially hidden by the keyboard
      if (selectedInputY + selectedInputHeight > visibleAreaBottom) {
        const scrollOffset = selectedInputY + selectedInputHeight - visibleAreaBottom + 20; // add padding

        // Scroll to keep input visible above keyboard
        if (group?.repeatable) {
          // For repeatable groups with SectionList
          listRef.current.scrollToLocation({
            animated: true,
            sectionIndex: 0,
            itemIndex: 0,
            viewOffset: scrollOffset,
          });
        } else {
          // For non-repeatable groups with FlatList
          listRef.current.scrollToOffset({
            animated: true,
            offset: scrollOffset,
          });
        }
      }
    });

    return () => {
      keyboardDidShowListener.remove();
    };
  }, [selectedInputY, selectedInputHeight, group?.repeatable]);

  useEffect(() => {
    if (listRef.current) {
      if (group?.repeatable) {
        listRef.current.scrollToLocation({
          animated: true,
          sectionIndex: 0,
          itemIndex: 0,
        });
      } else {
        // Do not automatically scroll to top on initial render
        // This prevents the auto-scrolling behavior that causes input fields to jump
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
          renderItem={({ item, section }) => {
            const fieldValue = values?.[item.id];

            return (
              <View key={`question-${item.id}`} style={styles.questionContainer}>
                <QuestionField
                  keyform={item.id}
                  field={item}
                  onChange={handleOnChange}
                  value={fieldValue}
                  questions={section.data}
                  onFieldFocus={handleInputFocus}
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
                questions={activeQuestions}
                onFieldFocus={handleInputFocus}
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
