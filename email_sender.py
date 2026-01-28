import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

CATEGORY_ICONS = {
    "技术进展": "🔬",
    "产品发布": "🚀",
    "大公司动向": "🏢",
    "投融资": "💰",
    "行业观点": "💬",
    "其他": "📌",
}


def render_email(events, template_path="email_template.html"):
    """Render aggregated events into the HTML email template."""
    template = Path(template_path).read_text(encoding="utf-8")

    event_count = len(events)
    date_str = datetime.now().strftime("%Y年%m月%d日")

    events_html = ""
    for i, event in enumerate(events, 1):
        category = event.get("category", "其他")
        icon = CATEGORY_ICONS.get(category, "📰")
        summary = event.get("summary", "")
        sources = event.get("sources", [])

        # Source links
        source_links = ""
        for src in sources:
            title = src.get("title", "")
            link = src.get("link", "#")
            source_name = src.get("source", "")
            source_links += (
                f'<a href="{link}" style="color:#667eea; text-decoration:none; font-size:12px;" target="_blank">'
                f'{title}</a>'
                f'<span style="font-size:11px; color:#aaa;"> [{source_name}]</span><br>'
            )

        events_html += f"""
<tr>
<td style="padding:16px 32px;">
  <div style="margin-bottom:4px;">
    <span style="font-size:13px; color:#667eea; font-weight:600;">{icon} {category}</span>
  </div>
  <p style="margin:0 0 8px; color:#333; font-size:14px; line-height:1.6;">
    {summary}
  </p>
  <div style="padding-left:8px; border-left:2px solid #eee;">
    {source_links}
  </div>
</td>
</tr>"""

        # Add separator between events (except last)
        if i < event_count:
            events_html += """
<tr>
<td style="padding:0 32px;">
  <hr style="border:none; border-top:1px solid #f0f0f0; margin:0;">
</td>
</tr>"""

    html = template.replace("{{date}}", date_str)
    html = html.replace("{{event_count}}", str(event_count))
    html = html.replace("{{events_html}}", events_html)

    return html


def send_email(html_content, subject=None):
    """Send email via SMTP using environment variables for configuration."""
    smtp_server = os.environ["SMTP_SERVER"]
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    receiver = os.environ["RECEIVER_EMAIL"]

    if subject is None:
        subject = f"AI News Daily Digest - {datetime.now().strftime('%Y-%m-%d')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = receiver

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [receiver], msg.as_string())
    else:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [receiver], msg.as_string())

    print(f"Email sent to {receiver}")
