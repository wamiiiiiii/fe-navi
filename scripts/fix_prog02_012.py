#!/usr/bin/env python3
"""
PROG02-012 ナイーブ文字列マッチ問題の修正

問題：解説と正解が論理矛盾している。
  - 問題：T="ABABCABAB", P="ABAB" で内側比較は何回？
  - 元の正解 b=10、解説 c で「i=0 で4回一致して return → 合計4回」と認めつつ「10回相当」とぼかしている

修正：論理的に正しい a=4 を正解とし、解説と選択肢を整合させる。
trace_steps も追加して比較1〜4回目をステップ実行できるようにする。
"""

import json
from pathlib import Path


FIXED_QUESTION = {
    "question_id": "FE-B-PROG02-012",
    "chapter_id": "B-prog-02",
    "category": "B",
    "difficulty": 2,
    "question_text": (
        "次の疑似言語はナイーブ法による文字列パターンマッチである。"
        "テキスト T = \"ABABCABAB\"（長さ 9）、パターン P = \"ABAB\"（長さ 4）を入力したとき、"
        "内側ループの文字比較（T[i + j] と P[j] の比較）が実行される総回数として最も適切なものはどれか。"
    ),
    "choices": [
        {"id": "a", "text": "4 回"},
        {"id": "b", "text": "5 回"},
        {"id": "c", "text": "10 回"},
        {"id": "d", "text": "24 回（n − m + 1 回 × m）"},
    ],
    "correct_answer": "a",
    "explanation": (
        "i = 0 のとき内側ループは T[0]=A=P[0]、T[1]=B=P[1]、T[2]=A=P[2]、T[3]=B=P[3] の 4 回連続で一致し、"
        "j = m = 4 となって直後の判定で return i が実行される。"
        "つまり外側ループは i = 0 で打ち切られ、内側比較が実行されるのはこの 4 回のみ。"
        "b の 5 回は終了判定（j < m）まで含めた誤算、"
        "c の 10 回は i = 0 で return が起きないと誤って残りの i を加算した値、"
        "d の 24 回は最悪計算量 (n − m + 1) × m を機械的に当てはめた誤りで、"
        "いずれも実際の動作とは異なる。"
    ),
    "related_terms": ["ナイーブ法", "文字列照合", "パターンマッチ"],
    "related_page_id": "B-prog-02-04",
    "tags": ["文字列処理", "トレース"],
    "pseudocode": (
        "■ 整数型: naiveMatch(文字型: T[], 文字型: P[])\n"
        "  整数型: n, m, i, j\n"
        "  n ← 要素数(T)\n"
        "  m ← 要素数(P)\n"
        "  ▲ i を 0 から n − m まで 1 ずつ増やす\n"
        "    j ← 0\n"
        "    ▲ j < m かつ T[i + j] = P[j]\n"
        "      j ← j + 1\n"
        "    ▲\n"
        "    ◆ j = m\n"
        "      return i\n"
        "    ◆\n"
        "  ▲\n"
        "  return −1"
    ),
    "trace_steps": [
        {"line": 5, "vars": {"T": "ABABCABAB", "P": "ABAB", "n": 9, "m": 4, "i": 0}},
        {"line": 6, "vars": {"i": 0, "j": 0}},
        {"line": 7, "vars": {"i": 0, "j": 0, "T[i+j]": "A", "P[j]": "A", "判定": "A = A → true", "比較回数": 1}},
        {"line": 8, "vars": {"j": 1, "比較回数": 1}},
        {"line": 7, "vars": {"j": 1, "T[i+j]": "B", "P[j]": "B", "判定": "B = B → true", "比較回数": 2}},
        {"line": 8, "vars": {"j": 2, "比較回数": 2}},
        {"line": 7, "vars": {"j": 2, "T[i+j]": "A", "P[j]": "A", "判定": "A = A → true", "比較回数": 3}},
        {"line": 8, "vars": {"j": 3, "比較回数": 3}},
        {"line": 7, "vars": {"j": 3, "T[i+j]": "B", "P[j]": "B", "判定": "B = B → true", "比較回数": 4}},
        {"line": 8, "vars": {"j": 4, "比較回数": 4}},
        {"line": 10, "vars": {"j": 4, "m": 4, "判定": "j = m → return i", "比較回数": 4}},
        {"line": 11, "vars": {"戻り値": 0, "比較回数の合計": 4, "結論": "i = 0 で完全一致したので比較は 4 回で打ち切られる"}},
    ],
}


def main() -> None:
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "questions.json"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    new_questions = []
    fixed = False

    # 対象問題を入れ替える（イミュータブルに新リスト作成）
    for q in questions:
        if q.get("question_id") == FIXED_QUESTION["question_id"]:
            new_questions.append(FIXED_QUESTION)
            fixed = True
        else:
            new_questions.append(q)

    if not fixed:
        print("エラー: PROG02-012 が見つかりませんでした")
        return

    new_data = {**data, "questions": new_questions}

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print("完了: PROG02-012 を修正しました（正解 b → a, 解説整合, trace_steps 12ステップ追加）")


if __name__ == "__main__":
    main()
