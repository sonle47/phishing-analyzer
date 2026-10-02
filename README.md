# Phishing Analyzer
- API docs (live): https://phishing-analyzer-gp2w.onrender.com/docs

> [!NOTE]
> The API runs on free tiers (Render for the API, Neon for the database).
> Render puts a free service to sleep after 15 minutes with no traffic, so the
> first request after a quiet spell can take about a minute while it wakes up.
> Every request after that is fast again. Please be patient for the first one.
>
> Every `/api/v1/...` endpoint needs an `X-API-Key` header, so the docs page
> loads for everyone but those endpoints answer `401` without the key. Only
> `/health` and `/demo/cases` are open to everyone.

That poster of the hacker , the one with the hoodie and the code glowing in neon, that’s what got me interested in cybersecurity. Then every AI tutorial I enrolled used the same example “Is this email phishing or not?” for classification. One of my important emails ended up in spam, so I decided to build a small backend that makes that decision on its own to answer whether an email is phishing as a practical project as well.

- How an email is really built, and which parts an attacker can fake
- What email security rules exist (SPF, DKIM, DMARC, Reply-To, link tricks) and
  how a mail provider reports them in the email headers
- How an API protects itself with a header (`X-API-Key`)
- How a model could learn the same thing from examples instead of hand-written
  rules?

It's a backend only, built with **FastAPI**. I test it with the built-in Swagger page (`/docs`) and with Postman.

## What it does

- You send it the raw source of an email (in Gmail: ⋮ → "Show original") as JSON.
- It reads the sender, subject, body and every link in the email.
- It checks the email against hand-written email security rules.
- It gives the email a risk score from 0 to 100 and a category: `malicious`,
  `suspicious`, `benign` or `unknown`.
- It saves the result as a **case** in a database (PostgreSQL on Neon) 
- You can list cases, create a case and update a case with status after scoring with validation

## Testing

## Running it
1. Backend (this is all you need locally; the defaults work):
   ```
   cd backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. Create `backend/.env`:
   ```
   API_KEY=pick-your-own-key
   DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
   ```
3. Open http://localhost:8000/docs

## Structure of the project

```mermaid
flowchart LR
    A["Postman or curl"] -->|"POST raw email with X-API-Key header"| B["FastAPI"]
    B --> C{"API key correct?"}
    C -->|"no"| D["401 Unauthorized"]
    C -->|"yes"| E["Parse the email: sender, subject, body, links, headers"]
    E --> F["Check the rules and collect signals"]
    F --> G["Score 0 to 100 and pick a category"]
    G --> H[("PostgreSQL on Neon, SQLite locally")]
    H --> I["Return the saved case as JSON"]
```

```
backend/
├── requirements.txt
└── app/
    ├── main.py              starts the app and creates the table
    ├── config.py            settings (DATABASE_URL, API_KEY)
    ├── db.py                database connection
    ├── models.py            the Case table
    ├── schemas.py           the shape of requests and responses
    ├── auth.py              the X-API-Key check
    ├── api/
    │   ├── analyze.py       POST /api/v1/analyze
    │   └── cases.py         list, get and update cases
    └── services/
        ├── email_parser.py  raw email to sender, subject, body, links
        ├── heuristics.py    the email security rules
        ├── scoring.py       score to category
        └── pipeline.py      ties the steps together
```

## What's next


## Data and credits
The practice data for the model is the
[Phishing Email Detection dataset](https://huggingface.co/datasets/zefang-liu/phishing-email-dataset)
on Hugging Face (LGPL-3.0), a copy of the
[original on Kaggle](https://www.kaggle.com/datasets/subhajournal/phishingemails)
by Cyber Cop. It's downloaded when the training script runs and is not stored in
this repo. It contains real scam emails, so I never click anything in it.
