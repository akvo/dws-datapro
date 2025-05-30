import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: 'https://dws-datapro.akvo.org/api/v1/device',
  apkURL: 'https://dws-datapro.akvo.org/app',
};

export default defaultBuildParams;
