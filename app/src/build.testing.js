import buildJson from './build.json';

const defaultBuildParams = {
  ...buildJson,
  serverURL: 'https://dws-datapro.akvotest.org/api/v1/device',
  apkURL: 'https://dws-datapro.akvotest.org/app',
};

export default defaultBuildParams;
