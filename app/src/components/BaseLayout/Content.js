import React from 'react';
import { View, ScrollView, TouchableOpacity } from 'react-native';
import Card from '../Card';
import Stack from '../Stack';

const Content = ({ children = null, data = [], columns = 1, action = null }) => {
  if (data?.length) {
    return (
      <ScrollView>
        <Stack row columns={columns}>
          {data?.map((d) =>
            action ? (
              <TouchableOpacity
                key={d?.id}
                type="clear"
                onPress={() => action(d?.id)}
                testID={`card-touchable-${d?.id}`}
              >
                <Card
                  title={d?.name}
                  subTitles={d?.subtitles}
                  submissionType={d?.submission_type}
                />
              </TouchableOpacity>
            ) : (
              <View key={d?.id} testID={`card-non-touchable-${d?.id}`}>
                <Card title={d?.name} subTitles={d?.subtitles} />
              </View>
            ),
          )}
        </Stack>
      </ScrollView>
    );
  }
  return (
    <Stack row columns={columns}>
      {children}
    </Stack>
  );
};

export default Content;
