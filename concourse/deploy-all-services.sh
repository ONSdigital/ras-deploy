#!/bin/bash -e

fly_alias=$1
pipeline=$2
space=$3

if [[ -z "${space}" ]]; then
	echo Usage: $0 fly_alias pipeline space
	exit 1
fi

jobs=$(fly -t "${fly_alias}" jobs -p "${pipeline}" | awk '{ print $1 }' | grep "\-${space}-deploy") 

for job in $jobs; do 
	echo Triggering job $job
	fly -t "${fly_alias}" trigger-job -j "${pipeline}/${job}"
done