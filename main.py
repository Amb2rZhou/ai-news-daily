#!/usr/bin/env python3
"""AI News Daily Digest - Main entry point."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from email_sender import render_email, send_email
from news_collector import collect_all
from news_summarizer import summarize


def main():
    # Load .env for local development
    load_dotenv()

    # Resolve config path relative to this script
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / "config.yaml"
    template_path = script_dir / "email_template.html"

    # Step 1: Collect news
    print("=" * 50)
    print("AI News Daily Digest")
    print("=" * 50)
    articles = collect_all(str(config_path))

    if not articles:
        print("No news collected today. Skipping email.")
        return

    # Step 2: Summarize and aggregate via AI
    print("\nSummarizing with AI...")
    events = summarize(articles)

    if not events:
        print("Failed to summarize news. Skipping email.")
        return

    # Step 3: Render email
    print("\nRendering email...")
    html = render_email(events, str(template_path))

    # Step 4: Send email
    required_env = ["SMTP_SERVER", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "RECEIVER_EMAIL"]
    missing = [v for v in required_env if not os.environ.get(v)]
    if missing:
        print(f"\n[ERROR] Missing environment variables: {', '.join(missing)}")
        print("Set them in .env (local) or GitHub Secrets (CI).")
        sys.exit(1)

    print("Sending email...")
    send_email(html)
    print("\nDone!")


if __name__ == "__main__":
    main()
