// eslint-disable-next-line import/no-unresolved
import { SERVER_URL, APK_URL, APP_NAME } from '@env';
import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: SERVER_URL,
  apkURL: APK_URL,
  appName: APP_NAME,
};

export default defaultBuildParams;
