"""AI News Summarizer - Uses Claude API to aggregate and summarize news events."""

import json
import os
import re

import anthropic


def summarize(articles):
    """
    Aggregate deduplicated articles into at most 10 events using Claude API.

    Args:
        articles: list of dicts with keys: title, summary, source, link

    Returns:
        list of event dicts: [{"summary": str, "category": str, "sources": [{"title": str, "link": str, "source": str}]}]
    """
    if not articles:
        return []

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set. Cannot summarize.")
        return []

    # Build article text for the prompt
    articles_text = ""
    for i, art in enumerate(articles, 1):
        articles_text += (
            f"{i}. Title: {art['title']}\n"
            f"   Summary: {art.get('summary', '')}\n"
            f"   Source: {art.get('source', '')}\n"
            f"   Link: {art.get('link', '')}\n\n"
        )

    prompt = f"""你是一个 AI 新闻编辑。下面是今天采集到的 AI 领域新闻列表。请你完成以下任务：

1. 将讲同一件事的新闻合并为一个"事件"。
2. 每个事件输出：
   - summary：中文总结（2-3 句话，简洁准确地描述这件事）
   - category：分类，从以下选项中选一个：技术进展、产品发布、大公司动向、投融资、行业观点、其他
   - sources：1-2 条最权威的来源链接（中文来源优先），每条包含 title、link、source
3. 按重要性排序，最多输出 10 个事件。
4. 只输出合法的 JSON 数组，不要输出任何其他内容。注意：JSON 字符串中的双引号必须用 \\" 转义。

输出格式（严格 JSON）：
[
  {{
    "summary": "中文总结内容",
    "category": "分类",
    "sources": [
      {{"title": "文章标题", "link": "https://...", "source": "来源名"}}
    ]
  }}
]

以下是今天的新闻列表：

{articles_text}"""

    client = anthropic.Anthropic(api_key=api_key)

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": "["},
                ],
            )
            response_text = "[" + message.content[0].text.strip()

            # Extract the JSON array
            response_text = _extract_json_array(response_text)

            events = json.loads(response_text)
            print(f"Summarized into {len(events)} events.")
            return events

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                print(f"[WARN] JSON parse failed (attempt {attempt + 1}), retrying...")
                continue
            print(f"[ERROR] Failed to parse Claude response as JSON: {e}")
            print(f"Response was: {response_text[:500]}")
            return []
        except Exception as e:
            print(f"[ERROR] Claude API call failed: {e}")
            return []

    return []


def _extract_json_array(text):
    """Extract a JSON array from text, handling bracket matching."""
    start = text.find("[")
    if start == -1:
        return text

    depth = 0
    in_string = False
    escape_next = False
    end = len(text)

    for i in range(start, len(text)):
        ch = text[i]
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    return text[start:end]
