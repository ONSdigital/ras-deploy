# ras-deploy

CI/CD pipeline for RAS services.

![pipeline](https://i.imgur.com/HA4ENhA.png)

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
1. Deploy the pipeline `fly -t lite set-pipeline -p ras-deploy -c concourse/ras-deploy.yml  --load-vars-from concourse/secrets.yml`
1. Go to <concourse-host>/teams/main/pipelines/ras-deploy e.g. http://localhost:8080/teams/main/pipelines/ras-deploy