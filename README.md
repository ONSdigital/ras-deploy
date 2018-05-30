# ras-deploy

CI/CD pipeline for RAS/RM services.

## Description

This pipeline is based off the Concourse Demo pipeline and uses the same approach to triggering deployments and the 
use of Cloudfoundry spaces.  For more details, see the [Concourse Demo pipeline README](https://github.com/ONSdigital/concourse-demo-pipeline).

## Maintaining pipelines
The pipeline or task files (which could live in the services repository) will need to be updated whenever there is a change
that will have an effect on the build or deployment change of a services. e.g.

* Adding/Removing/Changing environmental variables
* Build scripts added/removed
* Changing the docker image used to build
* A service is added/removed
* A github repository is renamed
* A service depends on a new Cloudfoundry service
* A change to how the acceptance tests run

## Deploying pipeline

1. Install fly cli
```bash
wget https://github.com/concourse/concourse/releases/download/v3.5.0/fly_darwin_amd64
chmod +x fly_darwin_amd64
sudo mv fly_darwin_amd64 /usr/local/bin/fly
```
1. Copy `secrets.yml.example` to `secrets.yml` (Do not git push this file)
1. Assign values to all secret variables
1. Login to concourse `fly -t ons login -c $concourse_url`
1. Deploy the pipeline `fly -t ons set-pipeline -p rasrm -c concourse/pipeline.yml  --load-vars-from concourse/secrets.yml`
1. Go to $concourse_url/teams/rasrm/pipelines/rasrm

## Known issues
* `pq: current transaction is aborted, commands ignored until end of transaction block
` when deploying services. This is a known bug in concourse https://github.com/concourse/concourse/issues/2224. Restart the job to resolve this.
