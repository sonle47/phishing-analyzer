from app.models import Case
from app.services import email_parser, heuristics, scoring


def build_case(submission):
    raw_eml = submission.raw_eml.replace("\x00", "")
    parsed_email = email_parser.parse_raw_eml(raw_eml)

    signals = heuristics.find_signals(
        parsed_email["sender"],
        parsed_email["sender_display_name"],
        parsed_email["subject"],
        parsed_email["body_text"],
        parsed_email["urls"],
        parsed_email["headers"],
    )
    score, category = scoring.get_score_and_category(signals)

    return Case(
        sender=parsed_email["sender"],
        subject=parsed_email["subject"],
        body=parsed_email["body_text"],
        urls=parsed_email["urls"],
        signals=signals,
        score=score,
        category=category,
        status="new",
    )


def create_case(db, submission):
    case = build_case(submission)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case
