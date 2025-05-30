/* eslint-disable no-console */
import * as FileSystem from 'expo-file-system';
import * as SQLite from 'expo-sqlite';
import * as Sentry from '@sentry/react-native';
import sql from '../database/sql';

const DIR_NAME = 'SQLite';

const createSqliteDir = async () => {
  /**
   * Setup sqlite directory to save cascades sqlite from server
   */
  if (!(await FileSystem.getInfoAsync(FileSystem.documentDirectory + DIR_NAME)).exists) {
    await FileSystem.makeDirectoryAsync(FileSystem.documentDirectory + DIR_NAME);
  }
};

const download = async (downloadUrl, fileUrl, update = false) => {
  const fileSql = fileUrl?.split('/')?.pop(); // get last segment as filename
  const pathSql = `${DIR_NAME}/${fileSql}`;
  const { exists } = await FileSystem.getInfoAsync(FileSystem.documentDirectory + pathSql);
  if (exists && update) {
    const existingDB = SQLite.openDatabaseSync(fileSql);
    existingDB.closeAsync();
    await existingDB.deleteAsync();
  }
  if (!exists || update) {
    await FileSystem.downloadAsync(downloadUrl, FileSystem.documentDirectory + pathSql, {
      cache: false,
    });
  }
};

const loadDataSource = async (source, id = null) => {
  try {
    const { file: cascadeName } = source;
    const db = SQLite.openDatabaseSync(cascadeName, { useNewConnection: true });
    const result = id
      ? await sql.getFirstRow(db, 'nodes', { id })
      : await sql.getEachRow(db, 'nodes');
    return [result, db];
  } catch (error) {
    Sentry.captureMessage('[cascades] Unable to load cascade sqlite');
    Sentry.captureException(error);
    return Promise.reject(error);
  }
};

const dropFiles = async () => {
  const Sqlfiles = await FileSystem.readDirectoryAsync(FileSystem.documentDirectory + DIR_NAME);
  Sqlfiles.forEach(async (file) => {
    if (file.includes('sqlite')) {
      const fileUri = `${FileSystem.documentDirectory}${DIR_NAME}/${file}`;
      await FileSystem.deleteAsync(fileUri);
    }
  });
  return Sqlfiles;
};

const cascades = {
  createSqliteDir,
  loadDataSource,
  download,
  dropFiles,
  DIR_NAME,
};

export default cascades;
