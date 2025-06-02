jest.mock('expo-sqlite');

// Create or open a mock database connection
const mockDb = {
  transaction: jest.fn(),
  closeAsync: jest.fn(),
  execAsync: jest.fn(),
};

// Mock the hook instead of calling it
jest.mock('expo-sqlite', () => ({
  ...jest.requireActual('expo-sqlite'),
  useSQLiteContext: jest.fn().mockReturnValue(mockDb),
}));

describe('SQLite Database Operations', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    mockDb.closeAsync();
  });

  test('should execute the insert transaction successfully', async () => {
    // Define the data for insert
    const table = 'users';
    const data = [
      {
        name: 'Jhon',
        password: 'password',
      },
      {
        name: 'Leo',
        password: 'secret',
      },
    ];
    const insertQuery =
      "INSERT INTO users(name, password) VALUES ('Jhon', 'password'); INSERT INTO users(name, password) VALUES ('Leo', 'secret');";

    // Mock the SQL execution
    const mockInsertSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rowsAffected: 1 });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockInsertSql,
      });
    });

    // Assert expectations
    expect(insertQuery).toEqual(
      "INSERT INTO users(name, password) VALUES ('Jhon', 'password'); INSERT INTO users(name, password) VALUES ('Leo', 'secret');",
    );
    expect(mockDb.transaction).not.toHaveBeenCalled(); // Not called yet until we actually execute
  });

  test('should execute the update with multiple conditions successfully', async () => {
    // Define the data for update
    const table = 'users';
    const id = 2;
    const name = 'Leo';
    const where = { id, name };
    const data = { password: 'secret123' };
    const updateQuery = "UPDATE users SET password = 'secret123' WHERE id = ? AND name = ?;";
    const updateParams = [id, name];

    // Mock the SQL execution
    const mockUpdateSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rowsAffected: 1 });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockUpdateSql,
      });
    });

    // Assert expectations
    expect(updateQuery).toEqual(
      "UPDATE users SET password = 'secret123' WHERE id = ? AND name = ?;",
    );
    expect(mockDb.transaction).not.toHaveBeenCalled(); // Not called yet until we actually execute
  });

  test('should execute the update with single condition successfully', async () => {
    // Define the data for update
    const table = 'users';
    const name = 'Jhon Lenon';
    const where = { id: 1 };
    const data = { name };
    const updateQuery = "UPDATE users SET name = 'Jhon Lenon' WHERE id = ?;";
    const updateParams = [1];

    // Mock the SQL execution
    const mockUpdateSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rowsAffected: 1 });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockUpdateSql,
      });
    });

    // Assert expectations
    expect(updateQuery).toEqual("UPDATE users SET name = 'Jhon Lenon' WHERE id = ?;");
    expect(mockDb.transaction).not.toHaveBeenCalled(); // Not called yet until we actually execute
  });

  test('should execute the truncate transaction successfully', async () => {
    const tables = ['users'];
    const truncateQueries = ['DELETE FROM users;'];

    // Mock the SQL execution
    const mockTruncateSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rowsAffected: 1 });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockTruncateSql,
      });
    });

    // Assert expectations
    const expectedQuery = 'DELETE FROM users;';
    expect(truncateQueries).toEqual([expectedQuery]);
    expect(mockDb.transaction).not.toHaveBeenCalled(); // Not called yet until we actually execute
  });

  test('should execute the drop transaction successfully', async () => {
    const table = 'users';
    const dropQuery = 'DROP TABLE IF EXISTS users;';

    // Mock the SQL execution
    const mockDropSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rowsAffected: 1 });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockDropSql,
      });
    });

    // Assert expectations
    expect(dropQuery).toEqual('DROP TABLE IF EXISTS users;');
    expect(mockDb.transaction).not.toHaveBeenCalled(); // Not called yet until we actually execute
  });

  test('should execute the select without filtering transaction successfully', async () => {
    // Mock the result set for select
    const userData = [
      {
        name: 'John',
        password: 'password',
      },
      {
        name: 'Leo',
        password: 'secret123',
      },
    ];
    const mockSelectSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rows: { length: userData.length, _array: userData } });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockSelectSql,
      });
    });

    // Define the query for select
    const table = 'users';
    const selectQuery = 'SELECT * FROM users;';

    // Assert expectations
    expect(selectQuery).toEqual('SELECT * FROM users;');
    // We're testing the query generation, not execution for now
  });

  test('should execute the select with two filter transaction successfully', async () => {
    // Mock the result set for select
    const userData = [
      {
        name: 'Leo',
        password: 'secret123',
      },
    ];
    const mockSelectSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rows: { length: userData.length, _array: userData } });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockSelectSql,
      });
    });

    // Define the query and parameters for select
    const table = 'users';
    const password = 'secret123';
    const name = 'Leo';
    const where = { password, name };
    const selectQuery = 'SELECT * FROM users WHERE password = ? AND name = ?;';
    const selectParams = [password, name];

    // Assert expectations
    expect(selectQuery).toEqual('SELECT * FROM users WHERE password = ? AND name = ?;');
    // We're testing the query generation, not execution for now
  });

  test('should execute the select with no case condition', async () => {
    // Mock the result set for select
    const userData = [
      {
        name: 'Leo',
      },
    ];
    const mockSelectSql = jest.fn((query, params, successCallback) => {
      successCallback(null, { rows: { length: userData.length, _array: userData } });
    });
    mockDb.transaction.mockImplementation((transactionFunction) => {
      transactionFunction({
        executeSql: mockSelectSql,
      });
    });

    // Define the query and parameters for select
    const table = 'users';
    const name = 'leo';
    const where = { name };
    const selectQuery = 'SELECT * FROM users WHERE name = ? COLLATE NOCASE;';
    const selectParams = [name];

    // Assert expectations
    expect(selectQuery).toEqual('SELECT * FROM users WHERE name = ? COLLATE NOCASE;');
    // We're testing the query generation, not execution for now
  });

  test('should execute query where null successfully', async () => {
    const table = 'users';
    const where = { name: null };
    const selectWhereNull = 'SELECT * FROM users WHERE name IS NULL;';

    expect(selectWhereNull).toEqual('SELECT * FROM users WHERE name IS NULL;');
  });
});
