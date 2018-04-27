#!/usr/bin/env bash

set -ex

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation

APPS=$(cf apps | cut -f 1 -d ' ' | tail -n +5)
for app in $APPS
do
	cf delete -fr "$app"
done

SERVICES=$(cf services | cut -f 1  -d ' ' | tail -n +5)
for service in $SERVICES
do
	cf delete-service -f "$service"
done
