variable "project_id" {}

variable "region" {}

variable "bucket_name" {
  description = "Nombre del bucket"
}

variable "storage_class" {
  description = "Clase de almacenamiento del Bucket"
}

variable "service_account_name" {
  description = "Nombre de la cuenta de servicio"
}