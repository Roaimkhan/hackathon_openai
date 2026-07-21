# TableSwap MVP — Architecture

## 1. Decision record

**Style:** modular monolith. One React client, one FastAPI API, one PostgreSQL database, and Supabase Storage for meal images. No microservices, queues, event buses, or separate AI service.

**Why:** this keeps the end-to-end demo simple to run, trace, and polish while preserving clear module boundaries for later growth.

## 2. System context

```text
React + TypeScript (Vite)
          |
          | REST / JSON
          v
FastAPI modular monolith
  Auth | Meals | Swaps | Search | AI | Storage
          |
          +-- PostgreSQL (application records)
          +-- Supabase Storage (meal images only)
          +-- OpenAI GPT-5.6 (all reasoning)
```

The frontend never communicates directly with PostgreSQL, Supabase Storage, or OpenAI. The API issues signed upload URLs (or performs a scoped upload) and stores only the resulting image URL.

## 3. Backend boundaries

```text
backend/app/
  api/              # routers; validation, auth dependency, HTTP response only
  core/             # settings, DB session, security, error handling
  models/           # SQLAlchemy persistence models
  schemas/          # Pydantic request/response contracts
  repositories/     # CRUD queries only; no business decisions or OpenAI
  services/         # business rules and transactions
  modules/
    auth/           # authentication service and routes
    meals/          # meal lifecycle and ownership rules
    swaps/          # request state transitions
    ai/             # the sole GPT-5.6 integration point
    search/         # filters, ranking orchestration, pagination
    storage/        # Supabase image upload abstraction
```

Dependency direction is strictly:

```text
router -> service -> repository -> database
                  -> AI service
                  -> storage service
```

Routers do not query repositories. Repositories do not call services, GPT, or storage. Services coordinate repositories and integrations through FastAPI dependency injection.

## 4. Frontend boundaries

```text
frontend/src/
  app/              # providers and app bootstrap
  components/       # presentational shared UI only
  features/
    auth/           # sign-up and login
    dashboard/      # nearby meal feed
    meals/          # upload and meal detail
    swaps/          # inbox and request actions
    search/         # natural-language search
    profile/        # current user summary
  services/         # typed API client and auth token handling
  routes/           # route composition and access guards
  lib/              # formatting and small UI utilities
```

Each feature owns its page, components, API functions, hooks, and types. Shared components must remain presentation-only; feature rules stay in the feature/service layer.

## 5. Domain model

All primary keys are UUIDs. All tables include `created_at` and `updated_at` timestamps.

| Table | Essential fields | Indexes / relationships |
|---|---|---|
| `users` | id, email, password_hash | unique email |
| `profiles` | user_id, display_name, location, latitude, longitude | FK users; geo fields indexed as needed |
| `taste_profiles` | user_id, preferences JSON | FK users, one-to-one |
| `meals` | id, owner_id, title, description, cuisine, spice_level, tags JSON, allergens JSON, analysis JSON, availability | FK users; owner, cuisine, created_at |
| `meal_images` | id, meal_id, public_url, storage_path, position | FK meals; meal_id |
| `swap_requests` | id, meal_id, requester_id, recipient_id, message, status | FKs; recipient_id/status and meal_id indexes |
| `swap_history` | id, swap_request_id, action, actor_id, details JSON | FKs; swap_request_id |

Only URLs and storage paths go in the database—never image binaries.

## 6. Core API surface

| Module | MVP endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Meals | `POST /meals`, `GET /meals/{id}`, `GET /meals/mine`, `POST /meals/{id}/image-upload` |
| Feed | `GET /feed` |
| Search | `GET /search?q=` |
| Swaps | `POST /swaps`, `GET /swaps`, `POST /swaps/{id}/accept`, `POST /swaps/{id}/reject` |

All responses use `{ "data": ..., "meta": ... }`; errors use `{ "error": { "code": ..., "message": ... } }` from a global exception handler.

## 7. AI contract

`AIService` is the only component allowed to invoke GPT-5.6. Every call requires a structured JSON schema and is validated before use.

| Capability | Input | Validated output |
|---|---|---|
| Meal analysis | image URL + optional user text | title, description, cuisine, spice level, dietary tags, allergens, taste notes |
| Compatibility | viewer taste profile + meal metadata + distance | score 0–100, short explanation |
| Search interpretation | natural-language query | cuisine, spice range, dietary tags, radius, sort intent |
| Taste-profile update | accepted/completed swap context | preference additions/removals |

If AI output is malformed or unavailable, the relevant action returns a friendly retryable error. It must not silently invent a compatibility score. A manually supplied meal title/description may still be saved if analysis fails, marked `analysis_status: pending` for a retry.

## 8. Key flows

### Meal upload and analysis

```text
User selects image
 -> client uploads to Supabase through API-issued scope
 -> client submits meal draft + image URL
 -> MealService asks AIService for structured analysis
 -> validate result
 -> MealRepository persists meal and image record
 -> return enriched meal card
```

### Nearby feed

```text
Dashboard opens
 -> SearchService obtains nearby candidate meals from repository
 -> AIService scores each candidate against viewer profile
 -> service sorts by score, then distance
 -> feed returns score and concise explanation
```

### Natural-language search

```text
Query: "spicy homemade food nearby"
 -> AIService extracts structured filters
 -> SearchRepository applies filters and radius
 -> AIService generates compatibility for returned candidates
 -> results are returned with applied filters
```

### Swap lifecycle

```text
pending -> accepted | rejected
accepted -> completed (optional lightweight confirmation)
```

Only the meal owner may accept or reject. The requester may create one request per available meal. Each transition writes a `swap_history` record.

## 9. Authentication and authorization

JWT bearer authentication is used for the MVP. The current-user dependency resolves the token once per request. Services enforce ownership; client-side route guards are UX only and never replace server checks.

## 10. Delivery scope

The first build is limited to the eight judge-visible outcomes: account access, image-backed meal creation, AI analysis, nearby feed, AI fit explanations, request/accept swap, natural-language search, and a polished responsive UI.

Out of scope: chat, payments, push notifications, social graphs, real-time websockets, complicated maps, multi-image galleries, and recommendation infrastructure beyond the request-time AI flow.

## 11. Implementation sequence

1. Establish FastAPI shell, database migrations/models, auth, and shared response/error conventions.
2. Finish meal image upload and GPT-5.6 structured analysis end to end.
3. Build the nearby feed and compatibility cards.
4. Implement swap request and acceptance lifecycle.
5. Implement natural-language search.
6. Polish responsive UI and verify the complete three-minute demo path.

No later phase begins until the preceding user journey works end to end.
