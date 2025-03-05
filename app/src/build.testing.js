import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: 'https://iwsims.akvotest.org/api/v1/device',
  apkURL: 'https://iwsims.akvotest.org/app',
};

export default defaultBuildParams;
