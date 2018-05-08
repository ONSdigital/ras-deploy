# ras-deploy

CI/CD pipeline for RAS/RM services.

## Description

The pipeline deploys all the way to the `prod` environment (Cloud Foundry space) via the `ci`, `latest` and
`preprod` environments. Deployments to `ci` and `latest` are continuous and trigger on every merge to `master`,
deployments to `preprod` and `prod` require manual triggers.

## Environments

| Space   | Usage                                                                                                                              |
|---------|------------------------------------------------------------------------------------------------------------------------------------|
| ci      | Used for running automated tests.  This environment is not intended to be interacted with manually unless debugging failing tests. |
| latest  | Used by devs for testing and exploring.  This is always up to date with the latest commit that passes the `ci` acceptance tests.   |
| preprod | Used for SIT and CAT testing. This doesn't change without manual intervention.                                                     |
| prod    | The live application.  Nothing can be deployed to `prod` without having first been deployed to `preprod`.                          |

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
