# ras-deploy

CI/CD pipeline for RAS services.

![pipeline](https://i.imgur.com/HA4ENhA.png)

## Deploying pipeline

1. Copy `secrets.yml.example` to `secrets.yml`
1. Assign values to all secret variables
1. Login to concourse `fly -t lite login -c $CONCOURSE_HOST`
1. Deploy the pipeline `./deploy-pipeline.sh`