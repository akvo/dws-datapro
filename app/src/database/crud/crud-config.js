import sql from '../sql';

const configQuery = () => {
  const id = 1;
  return {
    getConfig: async (db) => {
      try {
        const config = await sql.getFirstRow(db, 'config', { id });
        return config;
      } catch (err) {
        return false;
      }
    },
    addConfig: async (db, data = {}) => {
      try {
        const res = await sql.insertRow(db, 'config', { id, ...data });
        return res;
      } catch (err) {
        return false;
      }
    },
    updateConfig: async (db, data) => {
      const res = await sql.updateRow(db, 'config', { id }, data);
      return res;
    },
  };
};

const crudConfig = configQuery();

export default crudConfig;
