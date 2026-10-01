from app.models import Case
from app.services import email_parser, heuristics, scoring


def analyze_submission(submission):
    email = email_parser.parse_raw_eml(submission.raw_eml)

    signals = heuristics.evaluate(
        email["sender"],
        email["sender_display_name"],
        email["subject"],
        email["body_text"],
        email["urls"],
        email["headers"],
    )
    score, category = scoring.categorize(signals)

    return Case(
        sender=email["sender"],
        subject=email["subject"],
        body=email["body_text"],
        urls=email["urls"],
        signals=signals,
        score=score,
        category=category,
        status="new",
    )


def process_submission(db, submission):
    case = analyze_submission(submission)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case
