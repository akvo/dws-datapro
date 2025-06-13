#!/bin/sh

apk update
apk add git
echo "SERVER_URL=${BACKEND_IP_ADDRESS}" >.env
echo "APK_URL=${WEBDOMAIN}/app" >>.env
echo "SENTRY_ENV=${SENTRY_ENV}" >>.env
echo "SENTRY_DSN=${SENTRY_DSN}" >>.env
echo "SENTRY_AUTH_TOKEN=${SENTRY_AUTH_TOKEN}" >>.env
echo "APK_NAME=${APK_NAME}" >>.env
echo "APK_SHORT_NAME=${APK_SHORT_NAME}" >>.env

sed -i "s|\"name\": \".*\"|\"name\": \"${APK_NAME}\"|" app.json
sed -i "s|\"slug\": \".*\"|\"slug\": \"${APK_SHORT_NAME}-mobile\"|" app.json
# Convert any hyphens (-) to underscores (_) for Android package name
ANDROID_PACKAGE=$(echo ${APK_SHORT_NAME} | sed 's/-/_/g')
sed -i "s|\"package\": \"com\.akvo\..*\"|\"package\": \"com.akvo.${ANDROID_PACKAGE}\"|" app.json
sed -i "s|\"name\": \".*\"|\"name\": \"${APK_SHORT_NAME}-mobile\"|" package.json

yarn install
yarn start
