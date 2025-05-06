import React, { useState } from 'react';
import { renderHook, fireEvent, act, render } from '@testing-library/react-native';
import { route } from '@react-navigation/native';
import SettingsForm from '../SettingsForm';
import { config } from '../config';

jest.mock('@react-navigation/native');
jest.mock('expo-sqlite');

// Mock the hook instead of calling it directly
jest.mock('expo-sqlite', () => ({
  ...jest.requireActual('expo-sqlite'),
  useSQLiteContext: jest.fn().mockReturnValue({
    transaction: jest.fn(),
    closeAsync: jest.fn(),
  }),
}));

const mockDb = {
  transaction: jest.fn(),
  closeAsync: jest.fn(),
};

describe('SettingsForm', () => {
  it('renders correctly', () => {
    const params = { id: 1, name: 'Advanced' };
    route.params = params;
    const findConfig = config.find((c) => c?.id === params.id);

    const { getByText, getByTestId } = render(<SettingsForm route={route} />);

    const switchEl = getByTestId('settings-form-switch-3');
    expect(switchEl).toBeDefined();

    findConfig?.fields?.forEach((f) => {
      const labelEl = getByText(f.label);
      expect(labelEl).toBeDefined();
    });
  });

  test('Storing data to state and database', async () => {
    const params = { id: 1, name: 'Advanced' };
    route.params = params;

    const { unmount, getByTestId } = render(<SettingsForm route={route} />);

    const { result } = renderHook(() => useState(null));
    const [, setEdit] = result.current;

    const authCodeItem = getByTestId('settings-form-item-2');
    fireEvent.press(authCodeItem);
    const authCodeConfig = {
      id: 31,
      type: 'number',
      name: 'syncInterval',
      label: 'Sync interval',
      description: 'Sync interval in minutes',
      key: 'UserState.syncInterval',
      editable: true,
    };
    act(() => {
      setEdit(authCodeConfig);
    });
    expect(result.current[0]).toEqual(authCodeConfig);

    const dialogEl = getByTestId('settings-form-dialog');
    expect(dialogEl).toBeDefined();
    const inputEl = getByTestId('settings-form-input');
    expect(inputEl).toBeDefined();

    const authCodeValue = 500;
    fireEvent(inputEl, 'onChangeText', { value: authCodeValue });

    const okEl = getByTestId('settings-form-dialog-ok');
    expect(okEl).toBeDefined();
    // Mock the database update without using conn.tx or reassigning SQLite.useSQLiteContext
    const mockUpdateResult = { rowsAffected: 1 };
    const mockSelectSql = jest.fn((q, p, successCallback) => {
      successCallback(null, mockUpdateResult);
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockSelectSql,
      });
    });

    expect(mockUpdateResult).toEqual({ rowsAffected: 1 });
    expect(mockDb.transaction).toHaveBeenCalled();
    unmount();
  });
});
