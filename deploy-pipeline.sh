#!/usr/bin/env bash

fly -t lite set-pipeline -p ras-deploy -c concourse/ras-deploy.yml  --load-vars-from concourse/secrets.yml