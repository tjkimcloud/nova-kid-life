# ── SSM Parameter Store ───────────────────────────────────────────────────────
#
# All secrets are stored as SecureString parameters under /novakidlife/.
# Values are initialized to "PLACEHOLDER" — update them manually after first
# `terraform apply` or via the deploy runbook:
#
#   aws ssm put-parameter --name /novakidlife/openai/api-key \
#     --value "sk-..." --type SecureString --overwrite
#
# Terraform uses lifecycle { ignore_changes = [value] } so manual updates
# to parameter values are never overwritten by subsequent applies.

locals {
  ssm_params = {
    "supabase/url"                 = "Supabase project URL"
    "supabase/service-key"         = "Supabase service role key (secret)"
    "openai/api-key"               = "OpenAI API key for gpt-4o-mini and embeddings"
    "google/project-id"            = "Google Cloud project ID (Imagen 3)"
    "google/location"              = "Google Cloud region (e.g. us-central1)"
    "google/service-account-json"  = "Google service account JSON (base64 encoded)"
    "google/places-api-key"        = "Google Places API key for image sourcing"
    "media/bucket-name"            = "S3 media bucket name"
    "media/cdn-url"                = "Media CDN base URL (https://media.novakidlife.com)"
    "meetup/client-id"             = "Meetup OAuth client ID"
    "meetup/client-secret"         = "Meetup OAuth client secret"
    "ayrshare/api-key"             = "Ayrshare API key for social posting (replaced Buffer)"
    "unsplash/access-key"          = "Unsplash API access key for free stock photos"
    "pexels/api-key"               = "Pexels API key for free stock photos"
    "admin/api-key"                = "Admin API key for /admin/* endpoints"
  }
}

resource "aws_ssm_parameter" "novakidlife" {
  for_each = local.ssm_params

  name        = "/novakidlife/${each.key}"
  description = each.value
  type        = "SecureString"
  value       = "PLACEHOLDER"
  tier        = "Standard"

  lifecycle {
    # Never overwrite values set manually or by CI/CD
    ignore_changes = [value]
  }
}
