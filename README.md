````markdown
# PlateSwap

PlateSwap is an AI-powered community platform that lets neighbors exchange homemade meals with one another.

We've all experienced it—you come home and dinner is already prepared, but it's simply not what you're in the mood for. Maybe you've had the same meal multiple times this week, or you're craving something different. Instead of letting perfectly good homemade food go uneaten or ordering takeout, **PlateSwap lets you exchange your homemade meal with someone nearby who would love it, while enjoying something they've cooked instead.**

By combining local food sharing with AI, PlateSwap helps people discover new homemade dishes, reduce unnecessary food waste, and build stronger neighborhood communities.

One of PlateSwap's standout features is its **AI-powered meal analysis**. Instead of manually filling out long forms, users simply upload a photo of their meal. Our backend sends the image to **OpenAI's GPT-5.6 multimodal model**, which automatically understands the meal and generates structured information including:

- Meal title
- Natural language description
- Estimated calories
- Protein, carbohydrates, and fat
- Dietary tags (High Protein, Vegetarian, Vegan, Dairy-Free, Gluten-Free, etc.)

This dramatically reduces the effort required to create listings while producing consistent, informative meal descriptions for everyone.

Throughout development, **OpenAI Codex** played a major role in building PlateSwap. We used Codex extensively to accelerate development, scaffold APIs, generate React components, refactor code, troubleshoot backend integration issues, debug authentication flows, improve application architecture, and rapidly iterate on new features. By combining AI-assisted development with engineering decisions and testing, we were able to move from concept to a fully functional prototype within the hackathon timeframe.

---

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- PostgreSQL 14+ (local or hosted)
- An OpenAI API key for AI meal analysis and natural-language search
- A Supabase project and public Storage bucket for meal photo uploads (optional unless uploading images)

---

## 1. Create the database

Create an empty PostgreSQL database. For a local PostgreSQL installation:

```bash
createdb plateswap
```

The backend automatically creates the required tables on startup for local development.

---

## 2. Configure the backend

From the project root, create `backend/.env` (ignored by Git):

```dotenv
# Required
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/plateswap
JWT_SECRET_KEY=replace-with-a-long-random-secret

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6
OPENAI_TIMEOUT_SECONDS=20

# Supabase Storage
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_STORAGE_BUCKET=meal-images
```

For image uploads, create a **public** Supabase Storage bucket named `meal-images` (or update `SUPABASE_STORAGE_BUCKET` accordingly).

**Important:** Never expose your `SUPABASE_SERVICE_ROLE_KEY` to the frontend.

---

## 3. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API starts at:

```
http://localhost:8000
```

Verify the server:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "data": {
    "status": "ok"
  },
  "meta": {}
}
```

Interactive API documentation:

```
http://localhost:8000/docs
```

---

## 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (typically):

```
http://localhost:5173
```

To customize the backend URL, create:

```dotenv
frontend/.env.local
```

```dotenv
VITE_API_URL=http://localhost:8000/api/v1
```

Restart Vite after changing environment variables.

---

## AI Meal Analysis Pipeline

When a user uploads a meal photo:

1. The user drops an image into the meal upload interface.
2. The FastAPI backend securely receives the image.
3. The backend forwards the image to **OpenAI GPT-5.6**.
4. The model analyzes the meal and generates structured metadata.
5. PlateSwap automatically populates the listing with:
   - Meal title
   - Description
   - Estimated nutrition
   - Dietary tags
6. The completed meal listing becomes immediately searchable and available for nearby users to discover.

This AI-assisted workflow removes manual data entry and creates richer, more consistent meal listings.

---

## Common Commands

```bash
# Build the frontend
cd frontend && npm run build

# Preview the production build
cd frontend && npm run preview
```

---

## Troubleshooting

**Backend won't start**

- Verify `DATABASE_URL`.
- Ensure PostgreSQL is running.
- Confirm the database exists.

**Browser CORS errors**

Run the frontend from:

```
http://localhost:5173
```

or add your frontend origin to the backend CORS configuration.

**Meal image uploads fail**

- Configure all Supabase environment variables.
- Ensure the configured Storage bucket exists and is public.

**AI meal analysis unavailable**

Configure:

```
OPENAI_API_KEY
```

Without an API key, PlateSwap continues to function, but AI-powered meal understanding and natural-language search are unavailable.

---

For a deeper look at the system architecture, API structure, and application design, see **ARCHITECTURE.md**.
````
