import re
from urllib.parse import urlparse

URGENCY_PHRASES = [
    "urgent", "immediately", "verify your account", "suspended", "act now",
    "password will expire", "unusual activity", "click here", "confirm your identity",
    "limited time", "final notice", "wire transfer", "gift card",
]

URL_SHORTENER_DOMAINS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly"]


def get_auth_result(headers, check_name):
    auth_header = headers.get("Authentication-Results")
    if not auth_header:
        return None

    match = re.search(check_name + r"=(\w+)", auth_header, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


def find_signals(sender, sender_display_name, subject, body_text, urls, headers):
    signals = {}
    score = 0

    spf = get_auth_result(headers, "spf")
    dkim = get_auth_result(headers, "dkim")
    dmarc = get_auth_result(headers, "dmarc")
    signals["spf"] = spf
    signals["dkim"] = dkim
    signals["dmarc"] = dmarc

    auth_fail_count = 0
    for auth_result in [spf, dkim, dmarc]:
        if auth_result is not None and auth_result != "pass":
            auth_fail_count = auth_fail_count + 1
    score = score + auth_fail_count * 15

    reply_to = headers.get("Reply-To")
    reply_to_mismatch = False
    if reply_to and sender not in reply_to:
        reply_to_mismatch = True
    signals["reply_to_mismatch"] = reply_to_mismatch
    if reply_to_mismatch:
        score = score + 10

    display_name_spoof = False
    if sender_display_name:
        display_name = sender_display_name.lower()
        sender_domain = ""
        if "@" in sender:
            sender_domain = sender.split("@")[-1].lower()
        name_looks_like_website = re.search(r"[a-z0-9.-]+\.(com|net|org|io)", display_name)
        if name_looks_like_website and sender_domain != "" and sender_domain not in display_name:
            display_name_spoof = True
    signals["display_name_spoof"] = display_name_spoof
    if display_name_spoof:
        score = score + 15

    if body_text is None:
        body_text = ""
    subject_and_body = (subject + " " + body_text).lower()
    urgency_phrases_found = []
    for phrase in URGENCY_PHRASES:
        if phrase in subject_and_body:
            urgency_phrases_found.append(phrase)
    signals["urgency_phrases"] = urgency_phrases_found
    score = score + min(len(urgency_phrases_found) * 8, 24)

    shortened_urls = []
    for url in urls:
        if urlparse(url).netloc.lower() in URL_SHORTENER_DOMAINS:
            shortened_urls.append(url)
    signals["shortened_urls"] = shortened_urls
    signals["url_count"] = len(urls)
    score = score + min(len(shortened_urls) * 10, 20)

    ip_address_urls = []
    for url in urls:
        if re.match(r"https?://\d{1,3}(\.\d{1,3}){3}", url):
            ip_address_urls.append(url)
    signals["ip_literal_urls"] = ip_address_urls
    if len(ip_address_urls) > 0:
        score = score + 20

    if score > 100:
        score = 100
    signals["heuristic_score"] = round(float(score), 1)

    return signals
