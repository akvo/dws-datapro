/* eslint-disable react/no-array-index-key */
import React from 'react';
import { View } from 'react-native';
import { Text } from '@rneui/themed';
import styles from './styles';

const Titles = ({ items }) => (
  <View style={styles.heading} testID="center-layout-items">
    {items?.map((item, ix) => (
      <Text key={ix} h4>
        {item}
      </Text>
    ))}
  </View>
);
export default Titles;
