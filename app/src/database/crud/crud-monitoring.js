import sql from '../sql';

const monitoringQuery = () => ({
  syncForm: async (db, { formId, administrationId, lastUpdated, formJSON }) => {
    const rows = await sql.getFilteredRows(db, 'monitoring', { uuid: formJSON.uuid });
    if (rows.length) {
      const monitoringID = rows?.[0]?.id;
      const res = await sql.updateRow(db, 'monitoring', monitoringID, {
        administrationId,
        json: formJSON ? JSON.stringify(formJSON.answers).replace(/'/g, "''") : null,
      });
      return res;
    }
    const res = await sql.insertRow(db, 'monitoring', {
      formId,
      uuid: formJSON.uuid,
      name: formJSON?.datapoint_name || null,
      administrationId,
      json: formJSON ? JSON.stringify(formJSON.answers).replace(/'/g, "''") : null,
      syncedAt: lastUpdated, // store last updated instead of unnecessary current time
    });
    return res;
  },
  getTotal: async (db, formId, search) => {
    const querySQL = search.length
      ? `SELECT COUNT(*) AS count FROM monitoring where formId = ? AND name LIKE ? COLLATE NOCASE`
      : `SELECT COUNT(*) AS count FROM monitoring where formId = ? `;
    const params = search.length ? [formId, `%${search}%`] : [formId];
    const rows = await sql.executeQuery(db, querySQL, params);
    return rows?.length;
  },
  getFormsPaginated: async (db, { formId, search = '', limit = 10, offset = 0 }) => {
    let sqlQuery = 'SELECT * FROM monitoring WHERE formId = $1';
    const queryParams = [formId];

    if (search.trim() !== '') {
      sqlQuery += ' AND name LIKE $2 COLLATE NOCASE';
      queryParams.push(`%${search}%`);
    }

    sqlQuery += ' ORDER BY syncedAt DESC LIMIT $3 OFFSET $4';
    queryParams.push(limit, offset * limit); // Fix offset calculation
    const rows = await sql.executeQuery(db, sqlQuery, queryParams);
    return rows;
  },
});

const crudMonitoring = monitoringQuery();

export default crudMonitoring;
