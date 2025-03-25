import sql from '../sql';

const configQuery = () => {
  const id = 1;
  return {
    getConfig: async (db) => {
      try {
        const config = await sql.getFirstRow(db, 'config');
        return config;
      } catch {
        return false;
      }
    },
    addConfig: async (db, data = {}) => {
      const res = await sql.insertRow(db, 'config', data);
      return res;
    },
    updateConfig: async (db, data) => {
      const res = await sql.updateRow(db, 'config', data, { id });
      return res;
    },
  };
};

const crudConfig = configQuery();

export default crudConfig;
