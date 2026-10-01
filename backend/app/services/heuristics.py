import re
from urllib.parse import urlparse

URGENCY_WORDS = [
    "urgent", "immediately", "verify your account", "suspended", "act now",
    "password will expire", "unusual activity", "click here", "confirm your identity",
    "limited time", "final notice", "wire transfer", "gift card",
]

SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"]


def get_auth_result(headers, key):
    raw = headers.get("Authentication-Results")
    if not raw:
        raw = headers.get("authentication-results")
    if not raw:
        return None

    match = re.search(key + r"=(\w+)", raw, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


def evaluate(sender, sender_display_name, subject, body_text, urls, headers):
    signals = {}
    score = 0

    spf = get_auth_result(headers, "spf")
    dkim = get_auth_result(headers, "dkim")
    dmarc = get_auth_result(headers, "dmarc")
    signals["spf"] = spf
    signals["dkim"] = dkim
    signals["dmarc"] = dmarc

    auth_fail_count = 0
    for result in [spf, dkim, dmarc]:
        if result is not None and result != "pass":
            auth_fail_count = auth_fail_count + 1
    score = score + auth_fail_count * 15

    reply_to = headers.get("Reply-To")
    if not reply_to:
        reply_to = headers.get("reply-to")
    reply_to_mismatch = False
    if reply_to and sender not in reply_to:
        reply_to_mismatch = True
    signals["reply_to_mismatch"] = reply_to_mismatch
    if reply_to_mismatch:
        score = score + 10

    display_name_spoof = False
    if sender_display_name:
        name = sender_display_name.lower()
        domain = ""
        if "@" in sender:
            domain = sender.split("@")[-1].lower()
        looks_like_brand = re.search(r"[a-z0-9.-]+\.(com|net|org|io)", name)
        if looks_like_brand and domain != "" and domain not in name:
            display_name_spoof = True
    signals["display_name_spoof"] = display_name_spoof
    if display_name_spoof:
        score = score + 15

    if body_text is None:
        body_text = ""
    text = (subject + " " + body_text).lower()
    urgency_hits = []
    for word in URGENCY_WORDS:
        if word in text:
            urgency_hits.append(word)
    signals["urgency_phrases"] = urgency_hits
    score = score + min(len(urgency_hits) * 8, 24)

    shortened_urls = []
    for url in urls:
        if urlparse(url).netloc.lower() in SHORTENERS:
            shortened_urls.append(url)
    signals["shortened_urls"] = shortened_urls
    signals["url_count"] = len(urls)
    score = score + min(len(shortened_urls) * 10, 20)

    ip_urls = []
    for url in urls:
        if re.match(r"https?://\d{1,3}(\.\d{1,3}){3}", url):
            ip_urls.append(url)
    signals["ip_literal_urls"] = ip_urls
    if len(ip_urls) > 0:
        score = score + 20

    if score > 100:
        score = 100
    signals["heuristic_score"] = round(float(score), 1)

    return signals
