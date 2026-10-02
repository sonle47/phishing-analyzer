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
> `/health` is open to everyone.

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
I tested the phishing detector on **20 different emails**:
5 malicious, 5 suspicious, 5 benign and 5 with nothing suspicious. For each one I
worked out the score I expected first then compared with the one provided by the phishing analyzer. All 20 matched.

| Group | Scores | What those emails cover |
|---|---|---|
| Malicious (5) | 74 to 100 | Fake PayPal, bank and Microsoft emails, a CEO gift card scam and a prize scam. They all push you to act fast, and most of them fail the sender checks (SPF, DKIM, DMARC) |
| Suspicious (5) | 36 to 49 | A few warning signs, but nothing that settles it. For example a fake-looking sender name with a shortened link, or an urgent email that replies to a different address |
| Benign (5) | 8 to 31 | Normal emails with one small oddity, like a newsletter that replies to a different address or a sale that says "limited time". One scores 31, right under the 35 cutoff, on purpose |
| Nothing suspicious (5) | 0 | Ordinary emails in different formats: plain text, HTML only, no sender at all, a PDF attached, and one where every check passes. I wanted to see the detector stay calm and not crash |


### Database
<img width="1467" height="730" alt="image" src="https://github.com/user-attachments/assets/b3a2984f-2b8a-4b08-98e3-78d380fd0742" />



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
I'm building the next step in my own branch, `ml-model`. Right now the API only uses
my hand-written rules, and I want to add a model of my own that learns to tell
whether an email is phishing or not.

- I pull down thousands of labeled phishing and safe emails from a public dataset on
  Hugging Face, about 17,500 after cleaning out the empty and duplicate ones.
- I split them into 75% to train the model (13,152 emails) and 25% to test it
  (4,384 emails), so I can check how it does on emails it has never seen.
- I'm now implementing the model training. The plan is to run it together with the
  hand-written rules, so every email gets two opinions and I can compare them.

## Data and credits
The practice data for the model is the
[Phishing Email Detection dataset](https://huggingface.co/datasets/zefang-liu/phishing-email-dataset)
on Hugging Face (LGPL-3.0), a copy of the
[original on Kaggle](https://www.kaggle.com/datasets/subhajournal/phishingemails)
by Cyber Cop. It's downloaded when the training script runs and is not stored in
this repo. It contains real scam emails, so I never click anything in it.
