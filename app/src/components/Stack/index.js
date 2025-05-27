import React from 'react';
import { View } from 'react-native';
import styles from './styles';

const Stack = ({
  children = null,
  columns = 1,
  row = false,
  reverse = false,
  background = '#f9fafb',
  gap = 8, // Add gap prop with default value
}) => {
  let flexDir = row ? 'row' : 'column';
  flexDir += reverse ? '-reverse' : '';

  // Calculate width accounting for gaps between items
  const gapTotal = (gap * (columns - 1)) / columns;
  const itemWidth = `${100 / columns - gapTotal}%`;

  return (
    <View
      style={{
        ...styles.container,
        flexDirection: flexDir,
        backgroundColor: background,
      }}
      testID="stack-container"
    >
      {React.Children.map(children, (child, index) => {
        if (child) {
          return React.cloneElement(child, {
            style: {
              ...child?.props?.style,
              width: itemWidth,
              marginRight: (index + 1) % columns !== 0 ? gap : 0,
              marginBottom: gap,
            },
          });
        }
        return null;
      })}
    </View>
  );
};

export default Stack;
