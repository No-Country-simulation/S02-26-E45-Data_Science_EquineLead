ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: install-all test-api deploy-api lint run-data-pipeline run-etl run-prefect \
        run-app run-monitoring download-models \
        train-leads train-engine \
        register-models promote-models \
        dvc-pull dvc-push \
        terraform-deploy terraform-datalake terraform-api terraform-destroy

PATH_INFRA = infra/terraform
PATH_DEPLOY_API = ./deployment
IMAGE_TAG = $(shell git rev-parse --short HEAD)

# Environment

install-all:
	uv sync --all-groups

lint:
	uv run pre-commit autoupdate
	cmd /C "set PYTHONIOENCODING=utf-8 && uv run pre-commit run --all-files"

# App & Services

run-app:
	uv run streamlit run app/app.py --server.port 8520

run-prefect:
	docker compose -f deployment/docker-compose.yml up prefect-server

# Data Pipeline

run-data-pipeline:
	docker compose -f deployment/docker-compose.yml --profile pipeline up --build

run-etl:
	uv run python src/flows/etl/data_pipeline.py

dvc-pull:
	uv run dvc pull

dvc-push:
	uv run dvc push

# Training

train-leads:
	uv run python src/experiments/leads/train.py

train-engine:
	uv run python src/experiments/engine/train.py

# Model Registry

download-models:
	uv run python src/registry/download_production_models.py

register-models:
	uv run python src/registry/register_models.py

promote-models:
	uv run python src/registry/promote_to_production.py

# Monitoring

run-monitoring:
	uv run python src/monitoring/flow.py

# API

test-api:
	docker build -t $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG) -f $(PATH_DEPLOY_API)/Dockerfile.api .
	docker run -p 8080:8080 $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG)

deploy-api:
	docker build -t $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG) -f $(PATH_DEPLOY_API)/Dockerfile.api .
	docker push $(DOCKER_USERNAME)/equinelead-api:$(IMAGE_TAG)
	gcloud builds submit --config $(PATH_DEPLOY_API)/cloudbuild.yaml --substitutions=_DOCKERHUB_USERNAME=$(DOCKER_USERNAME),_IMAGE_TAG=$(IMAGE_TAG) --no-source

# Infrastructure

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
