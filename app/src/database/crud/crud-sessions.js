import sql from '../sql';

const sessionsQuery = () => ({
  selectLastSession: async (db) => {
    try {
      const rows = await sql.getEachRow(db, 'sessions');
      return rows?.[rows.length - 1];
    } catch (error) {
      return false;
    }
  },
  addSession: async (db, data = { token: '', passcode: '' }) => {
    const res = await sql.insertRow(db, 'sessions', data);
    return res;
  },
});

const crudSessions = sessionsQuery();

export default crudSessions;
