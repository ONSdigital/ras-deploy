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

See [here](https://digitaleq.atlassian.net/wiki/spaces/RASB/pages/458358937/RAS+RM+Concourse+Pipeline)

## Troubleshooting
### Known issues
* `pq: current transaction is aborted, commands ignored until end of transaction block
` when deploying services. This is a known bug in concourse https://github.com/concourse/concourse/issues/2224. Restart the job to resolve this.


### Job failed in pipeline
Sometimes a job might fail in the pipeline. You should first try to identify the problem by:
 
* Looking at the logs from the failing job in the Concourse UI
* Looking at the logs from the application(s) in Cloud Foundry / Docker
* Trying to replicate the issue locally with Docker
 
If you're still unable to resolve the problem then you can **'hijack'** into the container of the failing job in Concourse. 

In this example, we'll look at failing acceptance tests in the CI space of the pipeline. 

1. Using the Concourse fly CLI to connect to the ci-acceptance-tests job:
    ```
    fly -t ons hijack --job rasrm/ci-acceptance-tests
    ```
1. Choose the container you wish to connect to. In this example we want to connect to the container that runs the acceptance tests, which is `1`
    ```
        1: build #2, step: acceptance-test, type: task
        2: build #2, step: get-cf-database-uris, type: task
        3: build #2, step: notify, type: get
        4: build #2, step: notify, type: put
    ```
1. You can now edit whatever you like in this container because this only relates to the current job. Containers are only around for a short time after a build finishes so that we can connect to them. For example, you could edit a test file to log out additional information and run the following:
    ```bash
    source cf-database-env-vars/setenv.sh
    cd rasrm-acceptance-tests-source/
    make setup
    pipenv run behave acceptance_tests/features/<name_of_feature_to_investigate>.feature
    ```