import React from 'react';
import { SearchBar } from '@rneui/themed';
import Stack from '../Stack';
import PageTitle from './PageTitle';
import Content from './Content';

const BaseLayout = ({
  children,
  title = null,
  subTitle = null,
  search = { placeholder: null, show: false, value: null, action: null },
  leftComponent = null,
  leftContainerStyle = {},
  rightComponent = null,
  rightContainerStyle = {},
}) => (
  <Stack>
    {title && (
      <PageTitle
        text={title}
        subTitle={subTitle}
        {...{ leftComponent, leftContainerStyle, rightComponent, rightContainerStyle }}
      />
    )}
    {search.show && (
      <SearchBar
        placeholder={search.placeholder}
        value={search.value}
        onChangeText={search.action}
        testID="search-bar"
      />
    )}
    {children}
  </Stack>
);

BaseLayout.Content = Content;

export default BaseLayout;
