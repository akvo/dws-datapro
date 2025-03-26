/**
 * Creates a table if it does not already exist.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to create.
 * @param {Object} fields - An object representing the column names and their corresponding data types.
 * @returns {Promise<void>} A promise that resolves when the table has been created.
 */
const createTable = async (db, table, fields) => {
  const columns = Object.entries(fields)
    .map(([name, type]) => `${name} ${type}`)
    .join(', ');
  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS ${table} (
      ${columns}
    );
  `);
  const res = await db.getFirstAsync(`PRAGMA table_info(${table})`);
  return res;
};

/**
 * Updates a row in the specified table in the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to update the row in.
 * @param {number} id - The ID of the row to update.
 * @param {Object} values - An object representing the column names and their corresponding values to be updated.
 * @returns {Promise<void>} A promise that resolves when the row has been updated.
 */
const updateRow = async (db, table, id, values) => {
  const setClause = Object.keys(values)
    .map((key) => `${key} = ?`)
    .join(', ');
  const params = [...Object.values(values), id];
  await db.runAsync(`UPDATE ${table} SET ${setClause} WHERE id = ?`, ...params);
};

/**
 * Deletes a row from the specified table in the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to delete the row from.
 * @param {number} id - The ID of the row to delete.
 * @returns {Promise<void>} A promise that resolves when the row has been deleted.
 */
const deleteRow = async (db, table, id) => {
  await db.runAsync(`DELETE FROM ${table} WHERE id = ?`, id);
};

/**
 * Retrieves the first row from the specified table in the database with optional conditions.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to retrieve the first row from.
 * @param {Object} [conditions={}] - An object representing the conditions for filtering rows (optional).
 * @returns {Promise<Object>} A promise that resolves to the first row in the table.
 */
const getFirstRow = async (db, table, conditions = {}) => {
  const whereClause = Object.keys(conditions).length
    ? Object.keys(conditions)
        .map((key) => (conditions[key] === null ? `${key} IS NULL` : `${key} = ?`))
        .join(' AND ')
    : false;
  const params = Object.values(conditions);
  const query = `
    SELECT * FROM ${table}
    ${whereClause ? `WHERE ${whereClause}` : ''}
    LIMIT 1;
  `;
  const firstRow = await db.getFirstAsync(query, ...params);
  return firstRow;
};

/**
 * Inserts a row into the specified table in the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to insert the row into.
 * @param {Object} values - An object representing the column names and their corresponding values to be inserted.
 * @returns {Promise<void>} A promise that resolves when the row has been inserted.
 */
const insertRow = async (db, table, values) => {
  const columns = Object.keys(values).join(', ');
  const placeholders = Object.keys(values)
    .map(() => '?')
    .join(', ');
  const params = Object.values(values);
  await db.runAsync(`INSERT INTO ${table} (${columns}) VALUES (${placeholders})`, ...params);
};

/**
 * Retrieves all rows from the specified table in the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to retrieve all rows from.
 * @returns {Promise<Array>} A promise that resolves to an array of all rows in the table.
 */
const getEachRow = async (db, table) => {
  const rows = await db.getAllAsync(`SELECT * FROM ${table}`);
  return rows;
};

/**
 * Retrieves filtered rows from a specified table in the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to query.
 * @param {Object} conditions - An object representing the conditions for filtering rows.
 * @param {string} [orderBy=null] - The column name to order the results by (optional).
 * @param {string} [order='ASC'] - The order direction, either 'ASC' for ascending or 'DESC' for descending (optional).
 * @param {boolean} [collateNoCase=false] - Whether to use COLLATE NOCASE for case-insensitive matching (optional).
 * @returns {Promise<Array>} A promise that resolves to an array of filtered rows.
 */
const getFilteredRows = async (
  db,
  table,
  conditions,
  orderBy = null,
  order = 'ASC',
  collateNoCase = false,
) => {
  const whereClause = Object.keys(conditions)
    .map((key) => (conditions[key] === null ? `${key} IS NULL` : `${key} = ?`))
    .join(' AND ');
  const params = Object.values(conditions);
  const orderClause = orderBy ? `ORDER BY ${orderBy} ${order}` : '';
  const collateClause = collateNoCase ? 'COLLATE NOCASE' : '';
  const query = `
    SELECT * FROM ${table}
    WHERE ${whereClause} ${collateClause}
    ${orderClause};
  `;
  const rows = await db.getAllAsync(query, ...params);
  return rows;
};

/**
 * Executes a custom query on the database.
 *
 * @param {Object} db - The database connection object.
 * @param {string} query - The SQL query to execute.
 * @param {Array} [params=[]] - The parameters to pass to the query (optional).
 * @returns {Promise<Array>} A promise that resolves to the result of the query.
 */
const executeQuery = async (db, query, params = []) => {
  const result = await db.getAllAsync(query, ...params);
  return result;
};

/**
 * Drop a table from the database.
 * @param {Object} db - The database connection object.
 * @param {string} table - The name of the table to drop.
 * @returns {Promise<void>} A promise that resolves when the table has been dropped.
 */
const dropTable = async (db, table) => {
  await db.execAsync(`DROP TABLE IF EXISTS ${table}`);
};

const sql = {
  createTable,
  updateRow,
  deleteRow,
  getFirstRow,
  insertRow,
  getEachRow,
  getFilteredRows,
  executeQuery,
  dropTable,
};

export default sql;
