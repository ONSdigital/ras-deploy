#!/usr/bin/env bash

set -e

source cf-database-env-vars/setenv.sh

cd rasrm-acceptance-tests-source

make setup wait_for_services acceptance_tests