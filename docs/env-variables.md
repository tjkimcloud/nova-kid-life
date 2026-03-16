# Environment Variables — NovaKidLife

All secrets in production are stored in **AWS SSM Parameter Store** under the prefix `/novakidlife/`.
Never commit actual values. Never put secrets in Lambda environment variables directly.

---

## Frontend — `apps/web/.env.local`

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | API Gateway base URL | `https://api.novakidlife.com` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://xxxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase publishable (anon) key | `sb_publishable_...` (newer CLI) or `eyJ...` (older CLI) |
| `NEXT_PUBLIC_GA_ID` | Google Analytics measurement ID | `G-XXXXXXXXXX` |
| `NEXT_PUBLIC_SITE_URL` | Canonical site URL | `https://novakidlife.com` |

> `NEXT_PUBLIC_*` variables are embedded in the static bundle at build time — never put secrets here.

---

## API Lambda — `services/api/.env` (local dev only)

| Variable | SSM Path | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | `/novakidlife/supabase/url` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `/novakidlife/supabase/service-key` | Supabase secret (service role) key — `sb_secret_...` (newer CLI) or `eyJ...` (older CLI) |
| `OPENAI_API_KEY` | `/novakidlife/openai/api-key` | OpenAI key for embedding generation |
| `ALLOWED_ORIGINS` | `/novakidlife/api/allowed-origins` | CORS allowed origins (comma-separated) |
| `ADMIN_API_KEY` | `/novakidlife/api/admin-key` | API key for admin endpoints |
| `ENVIRONMENT` | — | `production` or `development` |

---

## Events Scraper Lambda — `services/events-scraper/.env` (local dev only)

| Variable | SSM Path | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | `/novakidlife/supabase/url` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `/novakidlife/supabase/service-key` | Supabase service role key |
| `EVENTS_QUEUE_URL` | `/novakidlife/sqs/events-queue-url` | SQS queue URL for raw events |
| `SCRAPER_SOURCES` | `/novakidlife/scraper/sources` | Comma-separated list of enabled sources |
| `MEETUP_CLIENT_ID` | `/novakidlife/meetup/client-id` | Meetup OAuth consumer key — register at meetup.com/api/oauth/list/ |
| `MEETUP_CLIENT_SECRET` | `/novakidlife/meetup/client-secret` | Meetup OAuth consumer secret |
| `ENVIRONMENT` | — | `production` or `development` |

---

## Image Gen Lambda — `services/image-gen/.env` (local dev only)

| Variable | SSM Path | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | `/novakidlife/supabase/url` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `/novakidlife/supabase/service-key` | Supabase service role key |
| `OPENAI_API_KEY` | `/novakidlife/openai/api-key` | OpenAI key for DALL-E 3 fallback |
| `GOOGLE_PROJECT_ID` | `/novakidlife/gcp/project-id` | GCP project for Vertex AI (Imagen 3) |
| `GOOGLE_LOCATION` | `/novakidlife/gcp/location` | Vertex AI region (e.g. `us-central1`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | `/novakidlife/gcp/service-account-json` | GCP service account key JSON |
| `MEDIA_BUCKET_NAME` | `/novakidlife/s3/media-bucket` | S3 bucket name for event images |
| `MEDIA_CDN_URL` | `/novakidlife/cdn/media-url` | CloudFront URL for media (e.g. `https://media.novakidlife.com`) |
| `IMAGE_PROVIDER` | — | `imagen3` or `dalle3` (overrides default) |
| `ENVIRONMENT` | — | `production` or `development` |

---

## Social Poster Lambda — `services/social-poster/.env` (local dev only)

| Variable | SSM Path | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | `/novakidlife/supabase/url` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `/novakidlife/supabase/service-key` | Supabase service role key |
| `BUFFER_ACCESS_TOKEN` | `/novakidlife/buffer/access-token` | Buffer API access token |
| `BUFFER_PROFILE_IDS` | `/novakidlife/buffer/profile-ids` | Comma-separated Buffer profile IDs (FB, IG, X) |
| `ENVIRONMENT` | — | `production` or `development` |

---

## Scheduler Lambda — `services/scheduler/.env` (local dev only)

| Variable | SSM Path | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | `/novakidlife/supabase/url` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `/novakidlife/supabase/service-key` | Supabase service role key |
| `SCRAPER_FUNCTION_NAME` | `/novakidlife/lambda/scraper-name` | Lambda function name for scraper |
| `EVENTS_QUEUE_URL` | `/novakidlife/sqs/events-queue-url` | SQS events queue URL |
| `ENVIRONMENT` | — | `production` or `development` |

---

## CI/CD — GitHub Actions Secrets

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user key for deployments |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret for deployments |
| `AWS_REGION` | AWS region (e.g. `us-east-1`) |
| `CLOUDFRONT_DISTRIBUTION_ID` | Web CloudFront distribution ID |
| `NEXT_PUBLIC_API_URL` | API URL baked into static build |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL baked into static build |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key baked into static build |
| `LHCI_GITHUB_APP_TOKEN` | Lighthouse CI GitHub token |

---

## SSM Parameter Store — Full Index

All production secrets live here. IAM roles grant Lambda read-only access to `/novakidlife/*`.

```
/novakidlife/
├── supabase/
│   ├── url                        (SecureString)
│   └── service-key                (SecureString)
├── openai/
│   └── api-key                    (SecureString)
├── gcp/
│   ├── project-id                 (String)
│   ├── location                   (String)
│   └── service-account-json       (SecureString)
├── buffer/
│   ├── access-token               (SecureString)
│   └── profile-ids                (String)
├── api/
│   ├── allowed-origins            (String)
│   └── admin-key                  (SecureString)
├── sqs/
│   └── events-queue-url           (String)
├── s3/
│   └── media-bucket               (String)
├── cdn/
│   └── media-url                  (String)
├── lambda/
│   └── scraper-name               (String)
└── aws/
    └── cloudfront-distribution-id (String)
```
