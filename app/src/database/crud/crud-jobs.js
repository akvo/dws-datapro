import sql from '../sql';
import crudUsers from './crud-users';

export const jobStatus = {
  PENDING: 1,
  ON_PROGRESS: 2,
  SUCCESS: 3,
  FAILED: 4,
};

export const MAX_ATTEMPT = 3;

export const SYNC_DATAPOINT_JOB_NAME = 'sync-form-datapoints';

const tableName = 'jobs';
const jobsQuery = () => ({
  getActiveJob: async (db, type) => {
    try {
      const session = await crudUsers.getActiveUser(db);
      if (session?.id) {
        /**
         * Make sure the app only gets active jobs from current user
         */
        const where = { type, user: session.id };
        const nocase = false;
        const orderBy = 'createdAt';
        const rows = await sql.getFilteredRows(db, tableName, where, orderBy, 'DESC', nocase);
        return rows;
      }
      return null;
    } catch {
      return null;
    }
  },
  addJob: async (db, data = {}) => {
    try {
      const createdAt = new Date().toISOString()?.replace('T', ' ')?.split('.')?.[0] || null;
      return await sql.insertRow(db, tableName, {
        ...data,
        createdAt,
      });
    } catch (error) {
      return Promise.reject(error);
    }
  },
  updateJob: async (db, id, data) => {
    try {
      return await sql.updateRow(db, tableName, id, data);
    } catch {
      return null;
    }
  },
  deleteJob: async (db, id) => {
    try {
      return await sql.deleteRow(db, tableName, id);
    } catch {
      return null;
    }
  },
});

const crudJobs = jobsQuery();

export default crudJobs;
