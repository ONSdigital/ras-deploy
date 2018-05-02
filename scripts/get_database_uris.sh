#!/usr/bin/env bash
set -e

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation >/dev/null

echo "export DATABASE_URI=$(cf apps | grep rm-case-service-ci-migration | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export PARTY_DATABASE_URI=$(cf apps | grep ras-party-ci-migration | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export DJANGO_OAUTH_DATABASE_URI=$(cf apps | grep django-oauth2-test-ci-migration | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export SECURE_MESSAGE_DATABASE_URI=$(cf apps | grep ras-secure-message-ci-migration | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
echo "export COLLECTION_INSTRUMENT_DATABASE_URI=$(cf apps | grep ras-collection-instrument-ci-migration | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')"
