.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: fly-performance-pipeline
fly-performance-pipeline: ## Fly the performance test pipeline
	fly -t ons set-pipeline \
		-p performance \
		-c pipelines/performance.yml \
		-l secrets/performance.yml
