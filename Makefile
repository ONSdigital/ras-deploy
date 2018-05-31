set_rasrm_pipeline:
	fly -t ${ONS_FLY_TARGET} set-pipeline -p rasrm -c concourse/pipeline.yml -l concourse/secrets.yml

set_loadtest_pipeline:
	fly -t ${ONS_FLY_TARGET} set-pipeline -p load-test -c concourse/loadtest-pipeline.yml -l concourse/secrets.yml -v loadtest_cloudfoundry_space=loadtest

set_loadtest2_pipeline:
	fly -t ${ONS_FLY_TARGET} set-pipeline -p loadtest2 -c concourse/loadtest-pipeline.yml -l concourse/secrets.yml -v loadtest_cloudfoundry_space=loadtest2

set_all_pipelines: set_rasrm_pipeline set_loadtest_pipeline set_loadtest2_pipeline