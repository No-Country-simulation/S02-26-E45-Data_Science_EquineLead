resource "google_storage_bucket" "equinelead-datalake" {
  name          = var.bucket_name
  location      = var.region
  storage_class = var.storage_class 
  force_destroy = true  # Permite borrar el bucket aunque tenga archivos (Cuidado en PROD)

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

data "google_service_account" "pipeline_sa" {
  account_id   = var.service_account_name
}

resource "google_storage_bucket_iam_member" "pipeline_sa_storage_admin" {
  bucket = google_storage_bucket.equine-lead-test.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.pipeline_sa.email}"
}

# Generar una nueva Key para esa cuenta (opcional)
resource "google_service_account_key" "pipeline_sa_key" {
  service_account_id = data.google_service_account.pipeline_sa.name
}

# Output para guardar la llave localmente (usar con precaución)
output "service_account_key" {
  value     = google_service_account_key.pipeline_sa_key.private_key
  sensitive = true
}

# Logueate en GCP:
# gcloud auth application-default login

# Ver el proyecto actual
# gcloud config get-value project

# Cambiar al proyecto correcto
# gcloud config set project TU_PROJECT_ID_AQUÍ

# Activar la API de IAM (Para crear la Service Account):
# gcloud services enable iam.googleapis.com

# Activar la API de Storage (Para crear el Bucket):
# gcloud services enable storage-api.googleapis.com

# Terraforma:
# terraform -chdir=infra/terraform init
# terraform -chdir=infra/terraform validate
# terraform -chdir=infra/terraform plan -out=tfplan
# terraform -chdir=infra/terraform apply "tfplan"
# terraform -chdir=infra/terraform destroy -auto-approve

# Error de cuenta
# $env:GOOGLE_APPLICATION_CREDENTIALS = $null