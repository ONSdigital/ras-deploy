#!/usr/bin/env bash
set -ex

function set_environment_variable {
    environment_var_name=$1
    environment_var_value=$2

    cf set-env "$APP_NAME" "$environment_var_name" "$environment_var_value"
}

function set_all_environment_variables {
    set_environment_variable RABBITMQ_AMQP_COLLECTION_INSTRUMENT "$RABBIT_URI"
    set_environment_variable RABBITMQ_AMQP_SURVEY_RESPONSE "$RABBIT_URI"
    set_environment_variable ONS_CRYPTOKEY "$ONS_CRYPTOKEY"
    set_environment_variable JSON_SECRET_KEYS "$JSON_SECRET_KEYS"
    set_environment_variable SECURITY_USER_NAME "$SECURITY_USER_NAME"
    set_environment_variable SECURITY_USER_PASSWORD "$SECURITY_USER_PASSWORD"
    set_environment_variable CASE_SERVICE_HOST "$CASE_SERVICE_HOST"
    set_environment_variable CASE_SERVICE_PORT "$CASE_SERVICE_PORT"
    set_environment_variable COLLECTION_EXERCISE_HOST "$COLLECTION_EXERCISE_HOST"
    set_environment_variable COLLECTION_EXERCISE_PORT "$COLLECTION_EXERCISE_PORT"
    set_environment_variable PARTY_SERVICE_HOST "$PARTY_SERVICE_HOST"
    set_environment_variable PARTY_SERVICE_PORT "$PARTY_SERVICE_PORT"
    set_environment_variable RM_SURVEY_SERVICE_HOST "$RM_SURVEY_SERVICE_HOST"
    set_environment_variable RM_SURVEY_SERVICE_PORT "$RM_SURVEY_SERVICE_PORT"
}


cd ras-collection-instrument-source

cf login -a "$CLOUDFOUNDRY_API" -u "$CLOUDFOUNDRY_EMAIL" -p "$CLOUDFOUNDRY_PASSWORD" -o "$CLOUDFOUNDRY_ORG" -s "$CLOUDFOUNDRY_SPACE" --skip-ssl-validation

cf push "$APP_NAME" --no-start
cf bind-service "$APP_NAME" "$SERVICE_NAME"

RABBIT_URI=$(cf apps | grep "$APP_NAME" | awk '{ print "cf env "$1 }'| bash | grep "amqp://" | head -1 | awk -F \" '{ print $4 }')

set_all_environment_variables

cf start "$APP_NAME"