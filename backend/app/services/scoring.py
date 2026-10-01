def categorize(signals):
    score = float(signals.get("heuristic_score", 0))
    score = round(score, 1)

    if score >= 70:
        category = "malicious"
    elif score >= 35:
        category = "suspicious"
    elif score > 0:
        category = "benign"
    else:
        category = "unknown"

    return score, category
