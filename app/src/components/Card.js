/* eslint-disable react/no-array-index-key */
import React from 'react';
import { Card as RneCard, Text } from '@rneui/themed';

const Card = ({ title = null, subTitles = [] }) => (
  <RneCard containerStyle={{ width: '100%' }}>
    {title && <RneCard.Title style={{ textAlign: 'left', width: '100%' }}>{title}</RneCard.Title>}
    {subTitles?.map((s, sx) => (
      <Text key={sx}>{s}</Text>
    ))}
  </RneCard>
);

export default Card;
