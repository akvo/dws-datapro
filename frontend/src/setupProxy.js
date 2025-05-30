const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    ["/api/**", "/static-files/**"],
    createProxyMiddleware({
      target: "http://localhost:8000",
      changeOrigin: true,
    })
  );
  app.use(
    ["/config.js"],
    createProxyMiddleware({
      target: "http://localhost:8000",
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        "^/config.js": "/api/v1/config.js",
      },
    })
  );
  app.use(
    ["/app"],
    createProxyMiddleware({
      target: "http://localhost:3000",
      changeOrigin: true,
      pathRewrite: {
        "^/app": "/apk/dws-datapro.apk",
      },
    })
  );
  app.use(
    ["/master-data"],
    createProxyMiddleware({
      target: "http://localhost:3000",
      changeOrigin: true,
      pathRewrite: {
        "^/master-data": "/master_data/fiji-administration.csv",
      },
    })
  );
};
