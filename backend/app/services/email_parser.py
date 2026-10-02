import re
from email import message_from_string, policy
from email.utils import parseaddr

from bs4 import BeautifulSoup

URL_PATTERN = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)


def extract_urls(text, html):
    urls = set()

    if text:
        for url in URL_PATTERN.findall(text):
            urls.add(url)

    if html:
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().startswith("http://") or href.lower().startswith("https://"):
                urls.add(href)
        for url in URL_PATTERN.findall(soup.get_text()):
            urls.add(url)

    return sorted(urls)


def html_to_text(html):
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def parse_raw_eml(raw_eml):
    message = message_from_string(raw_eml, policy=policy.default)

    body_text = None
    body_html = None

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            if content_type == "text/plain" and body_text is None:
                body_text = part.get_content()
            elif content_type == "text/html" and body_html is None:
                body_html = part.get_content()
    else:
        if message.get_content_type() == "text/html":
            body_html = message.get_content()
        else:
            body_text = message.get_content()

    if body_text is None and body_html is not None:
        body_text = html_to_text(body_html)

    display_name, sender_address = parseaddr(message.get("From", ""))

    sender = sender_address
    if not sender:
        sender = message.get("From", "unknown")

    parsed_email = {
        "sender": sender,
        "sender_display_name": display_name or None,
        "subject": message.get("Subject", "(no subject)"),
        "headers": message,
        "body_text": body_text,
        "urls": extract_urls(body_text, body_html),
    }
    return parsed_email
