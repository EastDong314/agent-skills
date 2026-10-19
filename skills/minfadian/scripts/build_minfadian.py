#!/usr/bin/env python3
"""Build a verbatim 《中华人民共和国民法典》 reference from an official HTML full text.

Design goal: keep the statute text byte-exact (only whitespace normalised) and add
navigation structure. Nothing is summarised or paraphrased.

Outputs:
  1. <vault>/法规/民法典/民法典全文.md      (frontmatter + 编/章/节 headings + 1260 条)
  2. <skill>/references/第N编-<名称>.md     (one file per 编, plus 附则)

Usage:
  python3 build_minfadian.py --html page.html
  python3 build_minfadian.py --url https://...   # downloads first

Verified 2026-09-20: the 1260 articles of this source are CJK-identical to the
新华社受权发布 text as published by 贵州人大 and 北京人大.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

DEFAULT_URL = "https://www.ah.gov.cn/zwyw/ztzl/xxxcgcmfd/ywjj/553989531.html"
DEFAULT_VAULT = Path(os.environ.get("OBSIDIAN_VAULT", Path.home() / "workspace" / "notes")).expanduser()
DEFAULT_SKILL = Path(__file__).resolve().parents[1]

CN_NUM = "零一二三四五六七八九十百千"
CN_DIGITS = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}

RE_BIAN = re.compile(rf"^第([{CN_NUM}]+)编\s+(\S.*)$")
RE_ZHANG = re.compile(rf"^第([{CN_NUM}]+)章\s+(\S.*)$")
RE_JIE = re.compile(rf"^第([{CN_NUM}]+)节\s+(\S.*)$")
RE_TIAO = re.compile(rf"^第([{CN_NUM}]+)条(?:\s+(.*))?$")

FOOTER_MARKERS = (
    "[ 我要纠错 ]",
    "扫一扫在手机打开当前页",
    "网站使用帮助",
    "网站地图",
    "ICP备",
    "公网安备",
    "不良信息举报",
    "中国互联网协会",
    "主办单位",
)

# 民法典 的 编 顺序（含附则），用于校验抽取结果是否完整
EXPECTED_BIAN = ["第一编 总则", "第二编 物权", "第三编 合同", "第四编 人格权",
                 "第五编 婚姻家庭", "第六编 继承", "第七编 侵权责任", "附则"]
EXPECTED_ZHANG = 84
EXPECTED_TIAO = 1260


def cn_to_int(text: str) -> int:
    """Parse a Chinese numeral up to 1299 (第二百五十九条, 第一千二百六十条, ...)."""
    if "百" in text or "千" in text:
        total = 0
        current = 0
        for ch in text:
            if ch in CN_DIGITS:
                current = CN_DIGITS[ch]
            elif ch == "十":
                total += (current or 1) * 10
                current = 0
            elif ch == "百":
                total += (current or 1) * 100
                current = 0
            elif ch == "千":
                total += (current or 1) * 1000
                current = 0
            else:
                raise ValueError(f"unexpected numeral char {ch!r} in {text!r}")
        return total + current
    if "十" in text:
        head, _, tail = text.partition("十")
        return (CN_DIGITS.get(head, 1)) * 10 + (CN_DIGITS.get(tail, 0) if tail else 0)
    return CN_DIGITS[text]


def read_source(url: str | None, path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    request = urllib.request.Request(url or DEFAULT_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - fixed https URL
        return response.read().decode("utf-8", errors="replace")


def strip_html(raw: str) -> list[str]:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    text = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</h\d>|</tr>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\u00a0\u3000]+", " ", text)
    return [line.strip() for line in text.split("\n") if line.strip()]


def is_footer(line: str) -> bool:
    return any(marker in line for marker in FOOTER_MARKERS)


def parse(lines: list[str]) -> dict:
    """Return the 编/章/节 structure and the ordered 1260 articles."""
    body_start = None
    seen_first_bian = False
    for index, line in enumerate(lines):
        if re.match(r"^第一编\s+总则$", line):
            if seen_first_bian:
                body_start = index  # second occurrence = body, first = 目录
                break
            seen_first_bian = True
    if body_start is None:
        raise SystemExit("找不到正文起点（第二处「第一编 总则」）")

    nodes: list[dict] = []          # ordered document nodes
    articles: dict[int, str] = {}
    current_bian = current_zhang = current_jie = None
    current_article: int | None = None

    for line in lines[body_start:]:
        if is_footer(line):
            break
        m = RE_BIAN.match(line)
        if m:
            current_bian = line
            current_zhang = current_jie = None
            current_article = None
            nodes.append({"kind": "bian", "text": line})
            continue
        m = RE_ZHANG.match(line)
        if m:
            current_zhang = line
            current_jie = None
            current_article = None
            nodes.append({"kind": "zhang", "text": line})
            continue
        m = RE_JIE.match(line)
        if m:
            current_jie = line
            current_article = None
            nodes.append({"kind": "jie", "text": line})
            continue
        if line == "附则":
            current_bian = "附则"
            current_zhang = current_jie = None
            current_article = None
            nodes.append({"kind": "bian", "text": "附则"})
            continue
        m = RE_TIAO.match(line)
        if m:
            number = cn_to_int(m.group(1))
            body = (m.group(2) or "").strip()
            prefix = line[: m.start(2)].rstrip() if m.group(2) else line
            if number in articles:
                raise SystemExit(f"第{number}条 重复出现")
            articles[number] = body
            current_article = number
            nodes.append({"kind": "tiao", "number": number, "prefix": prefix,
                          "text": f"{prefix} {body}".strip(),
                          "bian": current_bian, "zhang": current_zhang, "jie": current_jie})
            continue
        # Continuation of the current article (Chinese text wraps mid-sentence).
        if current_article is None:
            continue
        articles[current_article] = (articles[current_article] + line).strip()
        node = nodes[-1]
        node["text"] = f"{node['prefix']} {articles[current_article]}".strip()

    return {"nodes": nodes, "articles": articles}


def validate(parsed: dict) -> list[str]:
    articles: dict[int, str] = parsed["articles"]
    problems: list[str] = []
    missing = [n for n in range(1, EXPECTED_TIAO + 1) if n not in articles]
    if missing:
        problems.append(f"缺 {len(missing)} 条: {missing[:10]}")
    extra = [n for n in articles if n > EXPECTED_TIAO or n < 1]
    if extra:
        problems.append(f"超出范围的条号: {extra[:10]}")
    empty = [n for n, text in articles.items() if len(text.strip()) < 4]
    if empty:
        problems.append(f"正文为空/过短的条: {empty[:10]}")
    bian = [n["text"] for n in parsed["nodes"] if n["kind"] == "bian"]
    if bian != EXPECTED_BIAN:
        problems.append(f"编结构与预期不符: {bian}")
    zhang = [n["text"] for n in parsed["nodes"] if n["kind"] == "zhang"]
    if len(zhang) != EXPECTED_ZHANG:
        problems.append(f"章数量 {len(zhang)} != {EXPECTED_ZHANG}")
    if "自2021年1月1日起施行" not in articles.get(EXPECTED_TIAO, ""):
        problems.append("第一千二百六十条 未包含施行日期")
    if not articles.get(1, "").endswith("制定本法。"):
        problems.append("第一条 结尾异常")
    leaked = [n["text"][:40] for n in parsed["nodes"]
              if n["kind"] == "tiao" and is_footer(n["text"])]
    if leaked:
        problems.append(f"页脚内容混入正文: {leaked[:3]}")
    return problems


def render_body(parsed: dict) -> str:
    out: list[str] = []
    for node in parsed["nodes"]:
        if node["kind"] == "bian":
            out.append(f"\n## {node['text']}\n")
        elif node["kind"] == "zhang":
            out.append(f"\n### {node['text']}\n")
        elif node["kind"] == "jie":
            out.append(f"\n#### {node['text']}\n")
        else:
            out.append(node["text"] + "\n")
    return "\n".join(out).replace("\n\n\n", "\n\n").strip() + "\n"


def render_vault(parsed: dict, today: str) -> str:
    front = f"""---
title: "中华人民共和国民法典（全文）"
aliases:
  - "民法典"
  - "民法典全文"
  - "Civil Code of the People's Republic of China"
tags:
  - "法律"
  - "民法"
  - "民法典"
  - "参考资料"
related:
  - "[[民法典]]"
created: {today}
updated: {today}
type: "source"
status: "active"
source: "{DEFAULT_URL}"
promulgated: "2020-05-28"
effective: "2021-01-01"
articles: {EXPECTED_TIAO}
---

# 中华人民共和国民法典

> 2020年5月28日第十三届全国人民代表大会第三次会议通过，自2021年1月1日起施行。
> 全文 {EXPECTED_TIAO} 条，7 编 84 章，另附则。文本逐字取自官方公布版本，未作改写。
"""
    return front + "\n" + render_body(parsed) + """

---

## 相关链接

- [[民法典]]（结构导航、检索方式与数据校验说明）
- [[book-to-skill 调研与使用方式]]（为何没用书转 skill 流程，以及法条类资料的选型结论）

> 以上为逐字条文，取自安徽省人民政府网转发的新华社受权发布版本，并与贵州、北京人大两处官方全文逐条交叉校验。
> 本文件由 `~/.agents/skills/minfadian/scripts/build_minfadian.py` 生成，手工修改会在下次重建时被覆盖。
"""


def render_reference_files(parsed: dict) -> dict[str, str]:
    files: dict[str, tuple[str, list[str]]] = {}
    for node in parsed["nodes"]:
        if node["kind"] != "bian":
            continue
        name = node["text"]
        if name == "附则":
            slug = "附则"
        else:
            number = cn_to_int(RE_BIAN.match(name).group(1))
            title = RE_BIAN.match(name).group(2)
            slug = f"第{number}编-{title}"
        files.setdefault(slug, (name, []))

    slug_for: dict[str, str] = {}
    for node in parsed["nodes"]:
        if node["kind"] == "bian":
            name = node["text"]
            if name == "附则":
                slug_for[name] = "附则"
            else:
                m = RE_BIAN.match(name)
                slug_for[name] = f"第{cn_to_int(m.group(1))}编-{m.group(2)}"

    order: list[str] = []
    buckets: dict[str, list[str]] = {}
    current = None
    for node in parsed["nodes"]:
        if node["kind"] == "bian":
            current = slug_for[node["text"]]
            if current not in buckets:
                buckets[current] = []
                order.append(current)
            buckets[current].append(f"# {node['text']}\n")
        elif current is None:
            continue
        elif node["kind"] == "zhang":
            buckets[current].append(f"## {node['text']}\n")
        elif node["kind"] == "jie":
            buckets[current].append(f"### {node['text']}\n")
        else:
            buckets[current].append(node["text"] + "\n")

    return {slug: "\n".join(buckets[slug]).replace("\n\n\n", "\n\n").strip() + "\n" for slug in order}


def render_index(parsed: dict) -> str:
    """阿拉伯数字条号 → 中文条号 + 所在编/章，供 grep 直接定位。"""
    rows = [f"# 民法典条号速查（阿拉伯数字 → 中文条号 + 所在编/章）\n",
            "# 用法: grep \"^1042 \" 条号速查.md  →  得到「第一千零四十二条」与其所在编章\n"]
    by_number = {n["number"]: n for n in parsed["nodes"] if n["kind"] == "tiao"}
    for number in sorted(by_number):
        node = by_number[number]
        location = node["bian"] or ""
        if node["zhang"]:
            location += f" · {node['zhang']}"
        if node["jie"]:
            location += f" · {node['jie']}"
        rows.append(f"{number} | {node['prefix']} | {location}")
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--html", help="local HTML file instead of --url")
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lines = strip_html(read_source(args.url, args.html))
    parsed = parse(lines)
    problems = validate(parsed)
    articles = parsed["articles"]

    print(f"条数: {len(articles)} | 编: {sum(1 for n in parsed['nodes'] if n['kind'] == 'bian')}"
          f" | 章: {sum(1 for n in parsed['nodes'] if n['kind'] == 'zhang')}"
          f" | 节: {sum(1 for n in parsed['nodes'] if n['kind'] == 'jie')}")
    print(f"正文字符数: {sum(len(v) for v in articles.values())}")
    if problems:
        print("校验失败:")
        for problem in problems:
            print("  -", problem)
        return 1
    print("校验通过: 1260 条齐全、7 编 + 附则、84 章、首尾条文正确")

    if args.dry_run:
        return 0

    vault_file = args.vault / "法规/民法典/民法典全文.md"
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    vault_file.write_text(render_vault(parsed, date.today().isoformat()), encoding="utf-8")
    print("写入:", vault_file, f"({vault_file.stat().st_size} bytes)")

    refs = args.skill / "references"
    refs.mkdir(parents=True, exist_ok=True)
    for slug, content in render_reference_files(parsed).items():
        target = refs / f"{slug}.md"
        target.write_text(content, encoding="utf-8")
        print(f"写入: {target} ({target.stat().st_size} bytes)")

    index_file = refs / "条号速查.md"
    index_file.write_text(render_index(parsed), encoding="utf-8")
    print(f"写入: {index_file} ({index_file.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
