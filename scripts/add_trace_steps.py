#!/usr/bin/env python3
"""
科目B 疑似コード問題に trace_steps を付与するスクリプト

trace_steps の構造:
  {line: 1始まりの行番号, vars: {変数名: 値, ...}}

実行方法:
  cd fe_pwa && python3 scripts/add_trace_steps.py
"""

import json
from pathlib import Path

# 既存問題に trace_steps を埋めるマッピング
# キー: question_id, 値: trace_steps の配列
TRACE_DATA = {
    # ============================================================
    # PROG01-003: スタック (LIFO)
    # pseudocode:
    #  1: ■ stackOp()
    #  2:   変数宣言: 整数型: result
    #  3:   push(10)
    #  4:   push(20)
    #  5:   push(30)
    #  6:   pop()
    #  7:   push(40)
    #  8:   result ← pop()
    # ============================================================
    "FE-B-PROG01-003": [
        {"line": 2, "vars": {"result": "未定義", "stack": []}},
        {"line": 3, "vars": {"result": "未定義", "stack": [10]}},
        {"line": 4, "vars": {"result": "未定義", "stack": [10, 20]}},
        {"line": 5, "vars": {"result": "未定義", "stack": [10, 20, 30]}},
        {"line": 6, "vars": {"result": "未定義", "stack": [10, 20]}},
        {"line": 7, "vars": {"result": "未定義", "stack": [10, 20, 40]}},
        {"line": 8, "vars": {"result": 40, "stack": [10, 20]}},
    ],

    # ============================================================
    # PROG01-005: キュー (FIFO)
    # pseudocode:
    #  1: ■ queueOp()
    #  2:   変数宣言: 整数型: x
    #  3:   enqueue(7)
    #  4:   enqueue(3)
    #  5:   enqueue(9)
    #  6:   x ← dequeue()
    #  7:   enqueue(5)
    # ============================================================
    "FE-B-PROG01-005": [
        {"line": 2, "vars": {"x": "未定義", "queue": []}},
        {"line": 3, "vars": {"x": "未定義", "queue": [7]}},
        {"line": 4, "vars": {"x": "未定義", "queue": [7, 3]}},
        {"line": 5, "vars": {"x": "未定義", "queue": [7, 3, 9]}},
        {"line": 6, "vars": {"x": 7, "queue": [3, 9]}},
        {"line": 7, "vars": {"x": 7, "queue": [3, 9, 5]}},
    ],

    # ============================================================
    # PROG02-009: 再帰：階乗 fact(4)
    # pseudocode:
    #  1: ■ 整数型: fact(整数型: n)
    #  2:   ◆ n = 0
    #  3:     return 1
    #  4:   ◆
    #  5:   return n × fact(n − 1)
    # ============================================================
    # 再帰呼び出しのスタックを call_stack で表示し、
    # 戻り値が確定したら returns に積み上げる
    "FE-B-PROG02-009": [
        {"line": 1, "vars": {"n": 4, "call_stack": ["fact(4)"]}},
        {"line": 5, "vars": {"n": 4, "call_stack": ["fact(4)", "fact(3)"]}},
        {"line": 5, "vars": {"n": 3, "call_stack": ["fact(4)", "fact(3)", "fact(2)"]}},
        {"line": 5, "vars": {"n": 2, "call_stack": ["fact(4)", "fact(3)", "fact(2)", "fact(1)"]}},
        {"line": 5, "vars": {"n": 1, "call_stack": ["fact(4)", "fact(3)", "fact(2)", "fact(1)", "fact(0)"]}},
        {"line": 3, "vars": {"n": 0, "returns": "fact(0) = 1"}},
        {"line": 5, "vars": {"n": 1, "returns": "fact(1) = 1 × 1 = 1"}},
        {"line": 5, "vars": {"n": 2, "returns": "fact(2) = 2 × 1 = 2"}},
        {"line": 5, "vars": {"n": 3, "returns": "fact(3) = 3 × 2 = 6"}},
        {"line": 5, "vars": {"n": 4, "returns": "fact(4) = 4 × 6 = 24"}},
    ],

    # ============================================================
    # PROG02-001: 線形探索 target=18, A={12, 7, 25, 3, 18, 9}
    # pseudocode:
    #  1: ■ linearSearch(整数型: A[], 整数型: target)
    #  2:   整数型: i
    #  3:   ▲ i を 0 から 要素数(A) − 1 まで 1 ずつ増やす
    #  4:     ◆ A[i] = target
    #  5:       return i
    #  6:     ◆
    #  7:   ▲
    #  8:   return −1
    # ============================================================
    "FE-B-PROG02-001": [
        {"line": 2, "vars": {"A": [12, 7, 25, 3, 18, 9], "target": 18, "i": "未定義", "比較回数": 0}},
        {"line": 3, "vars": {"A": [12, 7, 25, 3, 18, 9], "target": 18, "i": 0, "比較回数": 0}},
        {"line": 4, "vars": {"i": 0, "A[i]": 12, "target": 18, "判定": "12 ≠ 18", "比較回数": 1}},
        {"line": 3, "vars": {"i": 1, "比較回数": 1}},
        {"line": 4, "vars": {"i": 1, "A[i]": 7, "target": 18, "判定": "7 ≠ 18", "比較回数": 2}},
        {"line": 3, "vars": {"i": 2, "比較回数": 2}},
        {"line": 4, "vars": {"i": 2, "A[i]": 25, "target": 18, "判定": "25 ≠ 18", "比較回数": 3}},
        {"line": 3, "vars": {"i": 3, "比較回数": 3}},
        {"line": 4, "vars": {"i": 3, "A[i]": 3, "target": 18, "判定": "3 ≠ 18", "比較回数": 4}},
        {"line": 3, "vars": {"i": 4, "比較回数": 4}},
        {"line": 4, "vars": {"i": 4, "A[i]": 18, "target": 18, "判定": "18 = 18 → return", "比較回数": 5}},
        {"line": 5, "vars": {"戻り値": 4, "比較回数": 5}},
    ],

    # ============================================================
    # PROG03-003: ループ累算 + if
    # pseudocode:
    #  1: 整数型: sum ← 0
    #  2: 整数型: i
    #  3: i を 1 から 5 まで 1 ずつ増やしながら繰り返す
    #  4:   もし (i mod 2 = 0) ならば
    #  5:     sum ← sum + i
    #  6:   ◆
    #  7: ▲
    #  8: sum を出力する
    # ============================================================
    "FE-B-PROG03-003": [
        {"line": 1, "vars": {"sum": 0, "i": "未定義"}},
        {"line": 3, "vars": {"sum": 0, "i": 1}},
        {"line": 4, "vars": {"sum": 0, "i": 1, "判定": "1 mod 2 = 1 → false"}},
        {"line": 3, "vars": {"sum": 0, "i": 2}},
        {"line": 4, "vars": {"sum": 0, "i": 2, "判定": "2 mod 2 = 0 → true"}},
        {"line": 5, "vars": {"sum": 2, "i": 2}},
        {"line": 3, "vars": {"sum": 2, "i": 3}},
        {"line": 4, "vars": {"sum": 2, "i": 3, "判定": "3 mod 2 = 1 → false"}},
        {"line": 3, "vars": {"sum": 2, "i": 4}},
        {"line": 4, "vars": {"sum": 2, "i": 4, "判定": "4 mod 2 = 0 → true"}},
        {"line": 5, "vars": {"sum": 6, "i": 4}},
        {"line": 3, "vars": {"sum": 6, "i": 5}},
        {"line": 4, "vars": {"sum": 6, "i": 5, "判定": "5 mod 2 = 1 → false"}},
        {"line": 8, "vars": {"sum": 6, "出力": 6}},
    ],
}


def main() -> None:
    """questions.json に trace_steps を追記する"""
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "data" / "questions.json"

    if not json_path.exists():
        print(f"エラー: {json_path} が見つかりません")
        return

    # 既存JSONを読み込む
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    if not questions:
        print("エラー: questions が空です")
        return

    updated = 0
    skipped = 0
    not_found = []

    # 対象問題に trace_steps を埋める（イミュータブルに新リスト作成）
    new_questions = []
    target_ids = set(TRACE_DATA.keys())
    found_ids = set()

    for q in questions:
        qid = q.get("question_id")
        if qid in TRACE_DATA:
            found_ids.add(qid)
            new_q = {**q, "trace_steps": TRACE_DATA[qid]}
            # tags に「トレース」を追加（既存になければ）
            tags = list(new_q.get("tags", []))
            if "トレース" not in tags:
                tags.append("トレース")
            new_q["tags"] = tags
            new_questions.append(new_q)
            updated += 1
        else:
            new_questions.append(q)

    not_found = list(target_ids - found_ids)

    if not_found:
        print(f"警告: 以下のID が見つかりませんでした: {not_found}")

    # バージョンを更新（科目B 拡充パッチを示す）
    new_data = {**data, "questions": new_questions}

    # 書き戻し（インデント2・日本語そのまま）
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"完了: {updated}問に trace_steps を付与しました")
    print(f"  対象: {sorted(found_ids)}")


if __name__ == "__main__":
    main()
