#!/bin/sh

apk update
apk add git
echo "SERVER_URL=${BACKEND_IP_ADDRESS}" >.env
echo "APK_URL=${WEBDOMAIN}/app" >>.env
echo "SENTRY_ENV=${SENTRY_ENV}" >>.env
echo "SENTRY_DSN=${SENTRY_DSN}" >>.env
echo "SENTRY_AUTH_TOKEN=${SENTRY_AUTH_TOKEN}" >>.env
echo "APP_NAME=${APP_NAME}" >>.env
echo "APP_SHORT_NAME=${APP_SHORT_NAME}" >>.env

sed -i "s|\"name\": \".*\"|\"name\": \"${APP_NAME}\"|" app.json

yarn install
yarn start
