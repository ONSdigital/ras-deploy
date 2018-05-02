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

OUTPUT=$(cf run-task "$APP_NAME" ./create_default_user.sh)
TASK_ID=$(echo "$OUTPUT" | tail -n 1 | sed 's/^task id:  *\([0-9]*\)/\1/')

echo "Ran task with ID: $TASK_ID"

RESULT=
while [[ -z "$RESULT" || $RESULT == "RUNNING" ]]; do
    RESULT=$(cf tasks "$APP_NAME" | grep "^$TASK_ID " | awk '{ print $3 }')
done

if [[ "$RESULT" == 'SUCCEEDED' ]]; then
    exit 0
else
    exit 1
fi