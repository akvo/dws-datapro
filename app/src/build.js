// eslint-disable-next-line import/no-unresolved
import { SERVER_URL, APK_URL, APK_NAME } from '@env';
import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: SERVER_URL,
  apkURL: APK_URL,
  apkName: APK_NAME,
};

export default defaultBuildParams;
