#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
レース結果PDF (天神祭奉納 / スモール選手権 等) を解析して
race_results.json を生成するスクリプト。

入力: PDF ファイル(複数指定可)
出力: race_results.json (大会別・レース別・レーン別)

依存:
    pip install pdfplumber

使い方:
    python3 parse_race_results.py path1.pdf path2.pdf ... -o race_results.json
"""
import argparse
import json
import os
import re
import sys
from datetime import date

try:
    import pdfplumber
except ImportError:
    print("[error] pdfplumber が必要です: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


# 大会名 → ID マッピング(PDF 上部から推定)
EVENT_MAP = [
    (re.compile(r"天神祭|日本国際"), "2025-11-02", "2025/11/02 天神祭奉納 日本国際選手権"),
    (re.compile(r"スモール.*日本選手権|第13回"), "2025-11-16", "2025/11/16 第13回 スモールドラゴンボート日本選手権"),
    (re.compile(r"KIX|ＫＩＸ"), "2025-10-05", "2025/10/05 第19回 KIX国際交流ドラゴンボート大会"),
]


def detect_event(pdf):
    """1ページ目のテキストから大会IDを推定"""
    text = pdf.pages[0].extract_text() or ""
    for pat, eid, name in EVENT_MAP:
        if pat.search(text):
            return eid, name
    return None, None


# 「区 分」列のセル: "第Nレース\nクラス\nステージ\n開始時刻"
RACE_HEADER_RE = re.compile(
    r"第\s*(\d+)\s*レース\s*\n\s*(.+?)\s*\n\s*(.+?)\s*\n\s*([\d:：]+)",
    re.MULTILINE,
)


def parse_race_header(cell):
    if not cell:
        return None
    m = RACE_HEADER_RE.search(cell)
    if not m:
        # フォールバック: 改行で分割
        parts = [p.strip() for p in cell.split("\n") if p.strip()]
        if not parts:
            return None
        rn_m = re.search(r"(\d+)", parts[0])
        if not rn_m:
            return None
        return {
            "race_no": f"R{int(rn_m.group(1))}",
            "class": parts[1] if len(parts) > 1 else "",
            "stage": parts[2] if len(parts) > 2 else "",
            "start_time": parts[3] if len(parts) > 3 else "",
        }
    return {
        "race_no": f"R{int(m.group(1))}",
        "class": m.group(2).strip(),
        "stage": m.group(3).strip(),
        "start_time": m.group(4).strip().replace("：", ":"),
    }


def clean_team_name(s):
    if not s:
        return ""
    s = s.strip()
    # 先頭の★や◯印を除去 (舵取り派遣など)
    s = re.sub(r"^[★☆◯●◎\s]+", "", s)
    return s


def parse_time(s):
    if not s or s == "-":
        return None
    s = s.strip()
    # "1:13.90" → 73.90 秒
    m = re.match(r"^(\d+):(\d+)\.(\d+)$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / (10 ** len(m.group(3)))
    # "73.90" 形式も対応
    try:
        return float(s)
    except ValueError:
        return None


def parse_int(s):
    if not s or s == "-":
        return None
    try:
        return int(s)
    except ValueError:
        return None


def parse_pdf(path):
    """PDF を解析してレース結果のリストを返す"""
    races = []
    with pdfplumber.open(path) as pdf:
        eid, ename = detect_event(pdf)
        if not eid:
            print(f"[warn] 大会IDが特定できません: {path}", file=sys.stderr)

        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                if not table or len(table) < 2:
                    continue
                header = table[0]
                # 期待するヘッダ: 区 分, ﾚｰﾝ, №, チーム名, タイム, 着順, 次レース組合せ
                if "区 分" not in (header[0] or ""):
                    continue
                current_race = None
                for row in table[1:]:
                    if not row or len(row) < 7:
                        continue
                    if row[0]:  # 区 分セルあり → 新しいレース
                        meta = parse_race_header(row[0])
                        if meta:
                            current_race = {
                                **meta,
                                "lanes": [],
                            }
                            races.append(current_race)
                    if not current_race:
                        continue
                    lane_raw, no_raw, team_raw, time_raw, rank_raw, next_raw = row[1:7]
                    lane = parse_int(lane_raw)
                    team_no = parse_int(no_raw)
                    team = clean_team_name(team_raw or "")
                    if not team or team == "-":
                        continue
                    current_race["lanes"].append({
                        "lane": lane,
                        "team_no": team_no,
                        "team": team,
                        "time_str": (time_raw or "").strip(),
                        "time_sec": parse_time(time_raw),
                        "rank": parse_int(rank_raw),
                        "next": (next_raw or "").strip(),
                    })

    return {"event_id": eid, "event_name": ename, "races": races}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+", help="解析するPDFファイル")
    ap.add_argument("-o", "--output", default="race_results.json")
    args = ap.parse_args()

    events = {}
    for path in args.pdfs:
        print(f"[parse] {path}")
        result = parse_pdf(path)
        eid = result["event_id"] or os.path.basename(path)
        if eid in events:
            # 同じ大会の複数PDF → races を結合
            existing_ids = {(r["race_no"], r["class"]) for r in events[eid]["races"]}
            for r in result["races"]:
                key = (r["race_no"], r["class"])
                if key not in existing_ids:
                    events[eid]["races"].append(r)
        else:
            events[eid] = result
        n_races = len(result["races"])
        n_lanes = sum(len(r["lanes"]) for r in result["races"])
        print(f"  → {n_races} レース / {n_lanes} レーン")

    output = {
        "title": "ドラゴンボート レース公式結果",
        "updated": date.today().isoformat(),
        "events": events,
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[ok] {args.output} を生成 ({len(events)} 大会)")


if __name__ == "__main__":
    main()
