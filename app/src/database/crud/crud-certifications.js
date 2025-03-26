import sql from '../sql';

const TABLE_NAME = 'certifications';

const certificationQuery = () => ({
  syncForm: async (db, { formId, administrationId, formJSON }) => {
    const rows = await sql.getFilteredRows(db, TABLE_NAME, { uuid: formJSON.uuid });
    if (rows.length) {
      const res = await sql.updateRow(db, TABLE_NAME, rows[0].id, {
        json: formJSON?.answers ? JSON.stringify(formJSON.answers).replace(/'/g, "''") : null,
        syncedAt: new Date().toISOString(),
      });
      return res;
    }
    const res = await sql.insertRow(db, TABLE_NAME, {
      formId,
      uuid: formJSON.uuid,
      name: formJSON?.datapoint_name || null,
      administrationId,
      json: formJSON?.answers ? JSON.stringify(formJSON.answers).replace(/'/g, "''") : null,
      syncedAt: new Date().toISOString(),
    });
    return res;
  },
  getTotal: async (db, formId, search, administrationId) => {
    let querySQL = search.length
      ? `SELECT COUNT(*) AS count FROM ${TABLE_NAME} where formId = ? AND name LIKE ? COLLATE NOCASE `
      : `SELECT COUNT(*) AS count FROM ${TABLE_NAME} where formId = ? `;
    const params = search.length ? [formId, `%${search}%`] : [formId];
    if (administrationId) {
      querySQL += ' AND administrationId = ? ';
      params.push(administrationId);
    }
    const rows = await sql.executeQuery(db, querySQL, params);
    return rows?.length;
  },
  getPagination: async (
    db,
    { formId, search = '', limit = 10, offset = 0, administrationId = null },
  ) => {
    let sqlQuery = `SELECT * FROM ${TABLE_NAME} WHERE formId = $1`;
    const queryParams = [formId];

    if (search.trim() !== '') {
      sqlQuery += ' AND name LIKE $2 COLLATE NOCASE';
      queryParams.push(`%${search}%`);
    }

    if (administrationId) {
      sqlQuery += ' AND administrationId = $3';
      queryParams.push(administrationId);
    }

    sqlQuery += ' ORDER BY syncedAt DESC LIMIT $4 OFFSET $5';
    queryParams.push(limit, offset * limit);
    const rows = await sql.executeQuery(db, sqlQuery, queryParams);
    return rows;
  },
  updateIsCertified: async (db, formId, uuid) => {
    try {
      const updateQuery = `UPDATE ${TABLE_NAME} SET isCertified = 1 WHERE formId = ? AND uuid = ?`;
      const params = [formId, uuid];
      return await sql.executeQuery(db, updateQuery, params);
    } catch {
      return null;
    }
  },
});

const crudCertification = certificationQuery();

export default crudCertification;
