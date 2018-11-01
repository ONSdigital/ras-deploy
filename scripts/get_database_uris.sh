#!/usr/bin/env bash
set -e

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation >/dev/null

retry_setup_env_var () {
  counter=1
  while [ 1 ]
  do
    EXPORT_VARIABLE=$1
    SERVICE_PREFIX=$2
      
    GET_URI_RESULT=$(cf apps | grep $SERVICE_PREFIX"$CLOUDFOUNDRY_SPACE" | awk '{ print "cf env "$1 }'| bash | grep "postgres://" | awk -F \" '{ print $4 }')
    
    stringlen=$(printf "%s" "$GET_URI_RESULT" | wc -c)
    if [ $stringlen -gt 0 ]
    then
      echo "export $EXPORT_VARIABLE=$GET_URI_RESULT"
      break
    fi
    
    if [ $counter -gt 3 ]
    then
      exit 1
    fi

    ((counter++))
    sleep 10
  done
}

retry_setup_env_var DATABASE_URI rm-case-service-
retry_setup_env_var PARTY_DATABASE_URI ras-party-
retry_setup_env_var DJANGO_OAUTH_DATABASE_URI django-oauth2-test-
retry_setup_env_var SECURE_MESSAGE_DATABASE_URI ras-secure-message-
retry_setup_env_var COLLECTION_INSTRUMENT_DATABASE_URI ras-collection-instrument-
