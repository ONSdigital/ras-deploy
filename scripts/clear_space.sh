#!/usr/bin/env bash

set -ev

cf login \
    -a "$CLOUDFOUNDRY_API" \
    -u "$CLOUDFOUNDRY_EMAIL" \
    -p "$CLOUDFOUNDRY_PASSWORD" \
    -o "$CLOUDFOUNDRY_ORG" \
    -s "$CLOUDFOUNDRY_SPACE" \
    --skip-ssl-validation

cf apps >/dev/null # Call this to check that the CF login command was successful

APPS=$(cf apps | cut -f 1 -d ' ' | tail -n +5)

if [ ${#APPS[@]} -ne 0 ]; then
    for app in $APPS
    do
     cf delete "$app" -f -r
    done
fi

SERVICES=$(cf services | cut -f 1 -d ' ' | tail -n +5)

if [ ${#SERVICES[@]} -ne 0 ]; then
    for service in $SERVICES
    do
     cf delete-service-key "$service" "$service"-key  -f
     cf delete-service "$service" -f
    done
fi
