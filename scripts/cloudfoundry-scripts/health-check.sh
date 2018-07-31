#!/usr/bin/env bash
set -e

#sdc-mock-gov-notify-sit

APPS=$(
cat <<EOM
ras-frontstage-api-sit
ras-party-sit
ras-secure-message-sit
rm-notify-gateway-sit
django-oauth2-test-sit
response-operations-ui-sit
iac-service-sit
rm-action-service-sit
ras-collection-instrument-sit
uaa-sit
rm-survey-service-sit
rm-sdx-gateway-sit
rm-case-service-sit
rm-collection-exercise-service-sit
rm-sample-service-sit
EOM
)

for app in $APPS; do
  echo "Checking $app"
  curl --silent --fail http://$app.apps.devtest.onsclofo.uk/info >/dev/null
done
