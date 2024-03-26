resource "google_iam_workload_identity_pool" "pool" {
  project                   = var.project_id
  workload_identity_pool_id = "pool"
}

resource "google_iam_workload_identity_pool_provider" "provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "provider"
  attribute_mapping = {
    "google.subject"    = "assertion.sub"
    "attribute.weather" = "assertion.weather.paris"
  }
  oidc {
    allowed_audiences = ["audience"]
    issuer_uri        = "https://some-address"
    jwks_json         = <<EOT
{"keys":[{"n":"3Mcw1mrl6fsRwKU5Ji9-nC2vxyuNXnehpT-wvMXpaErypBxlbOhHBIq1dF90QCs9mEHdW7o9rdwoslADmcBRc5k7Wrp2MhIbsfoR-R81Jm0sOyEX1sqKFrfm_tnHJHGWH6AMv5uVOyJv0h1Us7okwqhO58d6Bb26BSJzxhyk3CoN8IbJLH-y6MNjarqSULDeVbuZyuEtVAiinhnARsDNtdg8CkGaQOQATNBQVAQERvfDhGOo0OXrlZymeu7-6Q2Xkoo1kr6cvjaiScZp8j-csE2cOqL-SApBz8zPHzd1dl3YeJGNZ0JvJd6V8aSrFHlF1w20bzGJXu9qMDm6IY7NTw","e":"AQAB","kty":"RSA","use":"sig","alg":"RS256","kid":"S-kKjIe359QHombmMJoAMfnoV7G2LF-LguDZrw4D4rI"}]}
    EOT
  }
}

resource "google_service_account" "wi-sa" {
  account_id   = "wi-sa"
  display_name = "wi-sa"
  project      = var.project_id
}

resource "google_service_account_iam_binding" "wi-sa" {
  service_account_id = google_service_account.wi-sa.id
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.pool.name}/*",
    #"principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.pool.name}/attribute.weather/Sunny"
  ]
}

resource "google_project_iam_member" "wi-sa-pubsub-viewer" {
  project = var.project_id
  role    = "roles/pubsub.viewer"
  member  = "serviceAccount:${google_service_account.wi-sa.email}"
}