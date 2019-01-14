#!/usr/bin/env bash
set -e

#sdc-mock-gov-notify-perf

APPS=$(
cat <<EOM
ras-party-perf
ras-secure-message-perf
rm-notify-gateway-perf
django-oauth2-test-perf
response-operations-ui-perf
iac-service-perf
rm-action-service-perf
ras-collection-instrument-perf
uaa-perf
rm-survey-service-perf
rm-sdx-gateway-perf
rm-case-service-perf
rm-collection-exercise-service-perf
rm-sample-service-perf
EOM
)

for app in $APPS; do
  echo "Checking $app"
  curl --silent --fail http://$app.apps.devtest.onsclofo.uk/info >/dev/null
done
