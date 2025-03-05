import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: 'https://iwsims.akvo.org/api/v1/device',
  apkURL: 'https://iwsims.akvo.org/app',
};

export default defaultBuildParams;
