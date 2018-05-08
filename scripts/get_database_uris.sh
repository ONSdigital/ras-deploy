#!/usr/bin/env bash
set -e

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation >/dev/null

echo "export DATABASE_URI=$(cf apps | grep rm-case-service-"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export PARTY_DATABASE_URI=$(cf apps | grep ras-party-"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export DJANGO_OAUTH_DATABASE_URI=$(cf apps | grep django-oauth2-test-"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export SECURE_MESSAGE_DATABASE_URI=$(cf apps | grep ras-secure-message-"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export COLLECTION_INSTRUMENT_DATABASE_URI=$(cf apps | grep ras-collection-instrument-"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
