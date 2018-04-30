#!/usr/bin/env bash

set -ex

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation

APPS=$(cf apps | cut -f 1 -d ' ' | tail -n +5)
for app in $APPS
do
	cf delete "$app" -f -r
done

SERVICES=$(cf services | awk '{ print $1 }' | tail -n +5 | grep -v collection-instrument-rabbitmq)
for service in $SERVICES
do
 cf delete-service-key "$service" "$service"-key  -f
	cf delete-service "$service" -f
done