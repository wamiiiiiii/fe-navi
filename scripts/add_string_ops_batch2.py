#!/usr/bin/env python3
"""
科目B 新規問題 文字列処理バッチ2（3問）

PROG02-015: 文字列内の特定文字カウント
PROG02-016: パリンドローム判定（両端比較）
PROG02-017: 2文字列の最長共通接頭辞長さ

Sonnet 生成 → Opus レビュー（PROG02-016 の trace 行番号 line 11→12, line 12→13 を修正）
"""

import json
from pathlib import Path


NEW_QUESTIONS = [
    # ============================================================
    # PROG02-015 文字カウント（T="PROGRAM", c='R'）→ 2
    # ============================================================
    {
        "question_id": "FE-B-PROG02-015",
        "chapter_id": "B-prog-02",
        "category": "B",
        "difficulty": 1,
        "question_text": (
            "次の疑似言語プログラムは、文字配列 T の中から文字 c に一致する要素の個数を返す処理である。"
            "T = {'P','R','O','G','R','A','M'}（要素数 7）、c = 'R' を入力したときの戻り値はどれか。\n"
            "\n"
            "■ countChar(文字型: T[], 文字型: c)\n"
            "  整数型: i, cnt\n"
            "  cnt ← 0\n"
            "  ▲ i を 1 から 要素数(T) まで 1 ずつ増やす\n"
            "    ◆ T[i] = c\n"
            "      cnt ← cnt + 1\n"
            "    ◆\n"
            "  ▲\n"
            "  return cnt"
        ),
        "choices": [
            {"id": "a", "text": "1"},
            {"id": "b", "text": "2"},
            {"id": "c", "text": "3"},
            {"id": "d", "text": "0"},
        ],
        "correct_answer": "b",
        "explanation": (
            "cnt ← 0 で初期化し、i=1〜7 で T[i] = 'R' を判定する。"
            "i=1: 'P'≠'R'、i=2: 'R'='R' → cnt=1、i=3: 'O'≠'R'、i=4: 'G'≠'R'、"
            "i=5: 'R'='R' → cnt=2、i=6: 'A'≠'R'、i=7: 'M'≠'R'。"
            "ループ終了後、cnt=2 を返す。"
            "a の 1 は最初の 'R' で打ち切ったと誤解した off-by-one 誤り、"
            "c の 3 は他の文字を 'R' と誤認した計算ミス、"
            "d の 0 は条件 ≠ と取り違えて一致時にカウントしない誤りで、いずれも誤り。"
        ),
        "related_terms": ["文字列", "カウント", "ループ", "添字"],
        "related_page_id": "B-prog-02-04",
        "tags": ["文字列処理", "トレース", "ループ"],
        "pseudocode": (
            "■ countChar(文字型: T[], 文字型: c)\n"
            "  整数型: i, cnt\n"
            "  cnt ← 0\n"
            "  ▲ i を 1 から 要素数(T) まで 1 ずつ増やす\n"
            "    ◆ T[i] = c\n"
            "      cnt ← cnt + 1\n"
            "    ◆\n"
            "  ▲\n"
            "  return cnt"
        ),
        "trace_steps": [
            {"line": 3, "vars": {"cnt": 0, "T": "PROGRAM", "c": "R"}},
            {"line": 4, "vars": {"i": 1, "cnt": 0}},
            {"line": 5, "vars": {"i": 1, "T[i]": "P", "判定": "P = R → 偽"}},
            {"line": 4, "vars": {"i": 2, "cnt": 0}},
            {"line": 5, "vars": {"i": 2, "T[i]": "R", "判定": "R = R → 真"}},
            {"line": 6, "vars": {"i": 2, "cnt": 1}},
            {"line": 4, "vars": {"i": 3, "cnt": 1}},
            {"line": 5, "vars": {"i": 3, "T[i]": "O", "判定": "O = R → 偽"}},
            {"line": 4, "vars": {"i": 4, "cnt": 1}},
            {"line": 5, "vars": {"i": 4, "T[i]": "G", "判定": "G = R → 偽"}},
            {"line": 4, "vars": {"i": 5, "cnt": 1}},
            {"line": 5, "vars": {"i": 5, "T[i]": "R", "判定": "R = R → 真"}},
            {"line": 6, "vars": {"i": 5, "cnt": 2}},
            {"line": 4, "vars": {"i": 6, "cnt": 2}},
            {"line": 5, "vars": {"i": 6, "T[i]": "A", "判定": "A = R → 偽"}},
            {"line": 4, "vars": {"i": 7, "cnt": 2}},
            {"line": 5, "vars": {"i": 7, "T[i]": "M", "判定": "M = R → 偽"}},
            {"line": 9, "vars": {"戻り値": 2, "結論": "T 中に 'R' は 2 回出現"}},
        ],
    },

    # ============================================================
    # PROG02-016 パリンドローム判定（T="RACECAR", n=7）→ true
    # 行番号修正済み：line 11→12（ループ終端）、line 12→13（return）
    # ============================================================
    {
        "question_id": "FE-B-PROG02-016",
        "chapter_id": "B-prog-02",
        "category": "B",
        "difficulty": 2,
        "question_text": (
            "次の疑似言語プログラムは、文字配列 T が回文（前から読んでも後ろから読んでも同じ）かどうかを判定する処理である。"
            "T = {'R','A','C','E','C','A','R'}（要素数 7）を入力したときの戻り値はどれか。\n"
            "\n"
            "■ isPalindrome(文字型: T[])\n"
            "  整数型: n, half, i\n"
            "  論理型: result\n"
            "  n ← 要素数(T)\n"
            "  half ← n ÷ 2 の商\n"
            "  result ← true\n"
            "  ▲ i を 1 から half まで 1 ずつ増やす\n"
            "    ◆ T[i] ≠ T[n - i + 1]\n"
            "      result ← false\n"
            "      return result\n"
            "    ◆\n"
            "  ▲\n"
            "  return result"
        ),
        "choices": [
            {"id": "a", "text": "false"},
            {"id": "b", "text": "true"},
            {"id": "c", "text": "3"},
            {"id": "d", "text": "4"},
        ],
        "correct_answer": "b",
        "explanation": (
            "n=7、half=7÷2=3。両端から内側に向かって T[i] と T[n-i+1] を比較する。"
            "i=1: T[1]='R', T[7]='R' → 一致。"
            "i=2: T[2]='A', T[6]='A' → 一致。"
            "i=3: T[3]='C', T[5]='C' → 一致。"
            "i=4 は half=3 を超えるためループ終了。中央 T[4]='E' は単独要素なので比較不要。"
            "result は初期値の true のまま return される。"
            "a の false は不一致が見つかった場合の戻り値で、本入力ではすべて一致するため誤り。"
            "c の 3 は比較回数（half）を戻り値と混同した誤り。"
            "d の 4 は中央インデックスを戻り値と混同した誤り。"
            "戻り値は論理型 true。"
        ),
        "related_terms": ["回文", "パリンドローム", "両端比較", "文字列"],
        "related_page_id": "B-prog-02-04",
        "tags": ["文字列処理", "トレース", "回文", "両端比較"],
        "pseudocode": (
            "■ isPalindrome(文字型: T[])\n"
            "  整数型: n, half, i\n"
            "  論理型: result\n"
            "  n ← 要素数(T)\n"
            "  half ← n ÷ 2 の商\n"
            "  result ← true\n"
            "  ▲ i を 1 から half まで 1 ずつ増やす\n"
            "    ◆ T[i] ≠ T[n - i + 1]\n"
            "      result ← false\n"
            "      return result\n"
            "    ◆\n"
            "  ▲\n"
            "  return result"
        ),
        "trace_steps": [
            {"line": 4, "vars": {"T": "RACECAR", "n": 7}},
            {"line": 5, "vars": {"n": 7, "half": 3, "メモ": "7 ÷ 2 = 3（整数除算）"}},
            {"line": 6, "vars": {"result": True}},
            {"line": 7, "vars": {"i": 1, "half": 3}},
            {"line": 8, "vars": {"i": 1, "T[i]": "R", "T[n-i+1]": "T[7]=R", "判定": "R ≠ R → 偽"}},
            {"line": 7, "vars": {"i": 2}},
            {"line": 8, "vars": {"i": 2, "T[i]": "A", "T[n-i+1]": "T[6]=A", "判定": "A ≠ A → 偽"}},
            {"line": 7, "vars": {"i": 3}},
            {"line": 8, "vars": {"i": 3, "T[i]": "C", "T[n-i+1]": "T[5]=C", "判定": "C ≠ C → 偽"}},
            {"line": 12, "vars": {"i": 4, "メモ": "i=4 は half=3 を超えるのでループ終了"}},
            {"line": 13, "vars": {"戻り値": True, "結論": "全比較で一致 → true（回文）"}},
        ],
    },

    # ============================================================
    # PROG02-017 最長共通接頭辞長さ（S1="STATION", S2="STATIC"）→ 5
    # ============================================================
    {
        "question_id": "FE-B-PROG02-017",
        "chapter_id": "B-prog-02",
        "category": "B",
        "difficulty": 2,
        "question_text": (
            "次の疑似言語プログラムは、2 つの文字配列 S1, S2 の最長共通接頭辞の長さを返す処理である。"
            "S1 = {'S','T','A','T','I','O','N'}（要素数 7）、S2 = {'S','T','A','T','I','C'}（要素数 6）"
            "を入力したときの戻り値はどれか。\n"
            "\n"
            "■ commonPrefixLen(文字型: S1[], 文字型: S2[])\n"
            "  整数型: n1, n2, limit, i\n"
            "  n1 ← 要素数(S1)\n"
            "  n2 ← 要素数(S2)\n"
            "  ◆ n1 ≦ n2\n"
            "    limit ← n1\n"
            "  ◆\n"
            "  ◆ n1 > n2\n"
            "    limit ← n2\n"
            "  ◆\n"
            "  ▲ i を 1 から limit まで 1 ずつ増やす\n"
            "    ◆ S1[i] ≠ S2[i]\n"
            "      return i - 1\n"
            "    ◆\n"
            "  ▲\n"
            "  return limit"
        ),
        "choices": [
            {"id": "a", "text": "4"},
            {"id": "b", "text": "6"},
            {"id": "c", "text": "5"},
            {"id": "d", "text": "0"},
        ],
        "correct_answer": "c",
        "explanation": (
            "n1=7、n2=6 なので limit=min(n1,n2)=6。i を 1〜6 で動かし、最初の不一致位置の手前を返す。"
            "i=1: 'S'='S'、i=2: 'T'='T'、i=3: 'A'='A'、i=4: 'T'='T'、i=5: 'I'='I' まですべて一致。"
            "i=6: S1[6]='O'、S2[6]='C' → 不一致 → return i-1 = 5。"
            "a の 4 は i=5 で不一致と誤解した off-by-one 誤り、"
            "b の 6 は最後まで一致したと誤判定した誤り、"
            "d の 0 は最初から不一致と誤解した誤りで、いずれも誤り。"
        ),
        "related_terms": ["接頭辞", "文字列比較", "最長共通接頭辞", "ループ"],
        "related_page_id": "B-prog-02-04",
        "tags": ["文字列処理", "トレース", "接頭辞比較"],
        "pseudocode": (
            "■ commonPrefixLen(文字型: S1[], 文字型: S2[])\n"
            "  整数型: n1, n2, limit, i\n"
            "  n1 ← 要素数(S1)\n"
            "  n2 ← 要素数(S2)\n"
            "  ◆ n1 ≦ n2\n"
            "    limit ← n1\n"
            "  ◆\n"
            "  ◆ n1 > n2\n"
            "    limit ← n2\n"
            "  ◆\n"
            "  ▲ i を 1 から limit まで 1 ずつ増やす\n"
            "    ◆ S1[i] ≠ S2[i]\n"
            "      return i - 1\n"
            "    ◆\n"
            "  ▲\n"
            "  return limit"
        ),
        "trace_steps": [
            {"line": 3, "vars": {"S1": "STATION", "n1": 7}},
            {"line": 4, "vars": {"S2": "STATIC", "n2": 6}},
            {"line": 5, "vars": {"n1": 7, "n2": 6, "判定": "7 ≦ 6 → 偽"}},
            {"line": 8, "vars": {"判定": "7 > 6 → 真"}},
            {"line": 9, "vars": {"limit": 6, "メモ": "短い方を limit に"}},
            {"line": 11, "vars": {"i": 1, "limit": 6}},
            {"line": 12, "vars": {"i": 1, "S1[i]": "S", "S2[i]": "S", "判定": "S ≠ S → 偽"}},
            {"line": 11, "vars": {"i": 2}},
            {"line": 12, "vars": {"i": 2, "S1[i]": "T", "S2[i]": "T", "判定": "T ≠ T → 偽"}},
            {"line": 11, "vars": {"i": 3}},
            {"line": 12, "vars": {"i": 3, "S1[i]": "A", "S2[i]": "A", "判定": "A ≠ A → 偽"}},
            {"line": 11, "vars": {"i": 4}},
            {"line": 12, "vars": {"i": 4, "S1[i]": "T", "S2[i]": "T", "判定": "T ≠ T → 偽"}},
            {"line": 11, "vars": {"i": 5}},
            {"line": 12, "vars": {"i": 5, "S1[i]": "I", "S2[i]": "I", "判定": "I ≠ I → 偽"}},
            {"line": 11, "vars": {"i": 6}},
            {"line": 12, "vars": {"i": 6, "S1[i]": "O", "S2[i]": "C", "判定": "O ≠ C → 真"}},
            {"line": 13, "vars": {"戻り値": 5, "結論": "最初の 5 文字が共通"}},
        ],
    },
]


def main() -> None:
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "questions.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = list(data.get("questions", []))
    existing_ids = {q.get("question_id") for q in questions}

    added = 0
    for new_q in NEW_QUESTIONS:
        if new_q["question_id"] in existing_ids:
            print(f"スキップ（既存）: {new_q['question_id']}")
            continue
        questions.append(new_q)
        added += 1

    new_data = {**data, "questions": questions}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"完了: {added}問を追加（総数 {len(questions)}問）")


if __name__ == "__main__":
    main()
