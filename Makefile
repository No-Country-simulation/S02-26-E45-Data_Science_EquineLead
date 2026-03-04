-include .env
export

.PHONY: install lint run-data-pipeline run-prefect terraform-deploy terraform-destroy

PATH_INFRA = infra/terraform
PATH_DEPLOY_API = ./deployment
IMAGE_TAG = $(shell git rev-parse --short HEAD)

test-api:
	docker build -t $(DOCKER_USERNAME)/equinelead-api -f $(PATH_DEPLOY_API)/Dockerfile.api . 
	docker run -p 8080:8080 $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG)



deploy-api:
	docker build -t $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG) -f $(PATH_DEPLOY_API)/Dockerfile.api .
	docker push $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG)
	gcloud builds submit --config $(PATH_DEPLOY_API)/cloudbuild.yaml --substitutions=_DOCKERHUB_USERNAME=$(DOCKER_USERNAME),_IMAGE_TAG=$(IMAGE_TAG) --no-source

install:
	uv sync --locked

lint:
	pre-commit run --all-files

run-data-pipeline:
	docker compose -f deployment/docker-compose.yml --profile pipeline up --build

run-prefect:
	docker compose -f deployment/docker-compose.yml up prefect-server

terraform-deploy:
	terraform -chdir=$(PATH_INFRA) init
	terraform -chdir=$(PATH_INFRA) validate
	terraform -chdir=$(PATH_INFRA) plan -out=tfplan
	terraform -chdir=$(PATH_INFRA) apply "tfplan"

terraform-datalake:
	terraform -chdir=$(PATH_INFRA) init
	terraform -chdir=$(PATH_INFRA) validate
	terraform -chdir=$(PATH_INFRA) apply -target=google_storage_bucket.equinelead-datalake

terraform-api:
	terraform -chdir=$(PATH_INFRA) init
	terraform -chdir=$(PATH_INFRA) validate
	terraform -chdir=$(PATH_INFRA) apply -target=google_cloud_run_v2_service.equinelead_api -target=google_cloud_run_v2_service_iam_member.public_access

terraform-destroy:
	terraform -chdir=$(PATH_INFRA) destroy -auto-approve