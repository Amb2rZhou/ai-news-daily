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
    "其他": "📌",
}


def render_email(categorized_news, template_path="email_template.html"):
    """Render categorized news into the HTML email template."""
    template = Path(template_path).read_text(encoding="utf-8")

    total_count = sum(len(arts) for arts in categorized_news.values())
    category_count = len(categorized_news)
    date_str = datetime.now().strftime("%Y年%m月%d日")

    categories_html = ""
    for cat, articles in categorized_news.items():
        icon = CATEGORY_ICONS.get(cat, "📰")
        categories_html += f"""
<tr>
<td style="padding:16px 32px 4px;">
  <h2 style="margin:0; font-size:16px; color:#333; border-left:3px solid #667eea; padding-left:10px;">
    {icon} {cat}
    <span style="font-size:12px; color:#999; font-weight:normal; margin-left:6px;">({len(articles)})</span>
  </h2>
</td>
</tr>"""
        for art in articles:
            source = art.get("source", "")
            summary = art.get("summary", "")
            link = art.get("link", "#")
            title = art.get("title", "Untitled")

            summary_html = ""
            if summary:
                summary_html = f'<p style="margin:4px 0 0; color:#777; font-size:12px; line-height:1.5;">{summary}</p>'

            categories_html += f"""
<tr>
<td style="padding:6px 32px 6px 48px;">
  <a href="{link}" style="color:#333; text-decoration:none; font-size:14px; line-height:1.5;" target="_blank">
    {title}
  </a>
  <span style="font-size:11px; color:#aaa; margin-left:6px;">[{source}]</span>
  {summary_html}
</td>
</tr>"""

    html = template.replace("{{date}}", date_str)
    html = html.replace("{{total_count}}", str(total_count))
    html = html.replace("{{category_count}}", str(category_count))
    html = html.replace("{{categories_html}}", categories_html)

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
