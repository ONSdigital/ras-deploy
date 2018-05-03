# ras-deploy

CI/CD pipeline for RAS/RM services.

## Description

The pipeline deploys all the way to the `prod` environment (Cloud Foundry space) via the `ci`, `current` and
`preprod` environments. Deployments to `ci` and `current` are continuous and trigger on every merge to `master`,
deployments to `preprod` and `prod` require manual triggers.

## Environments

| Space   | Usage                                                                                                                              |
|---------|------------------------------------------------------------------------------------------------------------------------------------|
| ci      | Used for running automated tests.  This environment is not intended to be interacted with manually unless debugging failing tests. |
| current | Used by devs for testing and exploring.  This is always up to date with the latest commit that passes the `ci` acceptance tests.   |
| preprod | Used for SIT and CAT testing. This doesn't change without manual intervention.                                                     |
| prod    | The live application.  Nothing can be deployed to `prod` without having first been deployed to `preprod`.                          |

## Deploying pipeline

1. Install fly cli
```bash
wget https://github.com/concourse/concourse/releases/download/v3.5.0/fly_darwin_amd64
chmod +x fly_darwin_amd64
sudo mv fly_darwin_amd64 /usr/local/bin/fly
```
1. Copy `secrets.yml.example` to `secrets.yml`
1. Assign values to all secret variables
1. Login to concourse `fly -t lite login -c http://localhost:8080`
1. Deploy the pipeline `fly -t lite set-pipeline -p ras-deploy -c concourse/pipeline.yml  --load-vars-from concourse/secrets.yml`
1. Go to <concourse-host>/teams/main/pipelines/ras-deploy e.g. http://localhost:8080/teams/main/pipelines/ras-deploy
