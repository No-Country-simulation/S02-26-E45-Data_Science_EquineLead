.PHONY: install lint run-data-pipeline run-prefect terraform-deploy terraform-destroy

PATH_INFRA = infra/terraform

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

terraform-destroy:
	terraform -chdir=$(PATH_INFRA) destroy -auto-approve