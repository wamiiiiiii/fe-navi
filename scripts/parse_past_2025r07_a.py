#!/usr/bin/env python3
"""
令和7年度（2025r07）基本情報技術者試験 科目A 公開問題 20問を
pdftotext で抽出済みのテキストから構造化 JSON へ変換し、
questions.json の末尾に追記する。

入力:
  data/past_exams/2025r07/2025r07_fe_kamoku_a_qs.txt   # 問題本文
  data/past_exams/2025r07/2025r07_fe_kamoku_a_ans.txt  # 解答（ア/イ/ウ/エ）

出力:
  data/questions.json に 20問追記（chapter_id="PAST-2025r07-A", source="past_R07_FE_A"）

注意:
  - 図/表を含む問題（問3=2分探索木、問6=商品テーブル、問14=PERT図、問19=客席表）は
    本文中に「※元問題には図/表が含まれます。詳細はIPA公開PDFを参照」と注記する
  - 選択肢は 'a','b','c','d' に正規化（'ア'→'a', 'イ'→'b', 'ウ'→'c', 'エ'→'d'）
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PDF_DIR = BASE_DIR / "data" / "past_exams" / "2025r07"
QS_TXT = PDF_DIR / "2025r07_fe_kamoku_a_qs.txt"
ANS_TXT = PDF_DIR / "2025r07_fe_kamoku_a_ans.txt"
QUESTIONS_JSON = BASE_DIR / "data" / "questions.json"

# ア/イ/ウ/エ → a/b/c/d
KANA_TO_ID = {"ア": "a", "イ": "b", "ウ": "c", "エ": "d"}

# 図/表を含む問題（手動指定。元PDF参照を促す注記を本文末に追加）
HAS_FIGURE = {3, 6, 14, 19}

# 各問の出題分野タグ（手動分類）
QUESTION_TAGS = {
    1: ("テクノロジ系", ["AI", "ファインチューニング", "機械学習"]),
    2: ("テクノロジ系", ["浮動小数点", "丸め誤差", "情報の表現"]),
    3: ("テクノロジ系", ["2分探索木", "データ構造"]),
    4: ("テクノロジ系", ["稼働率", "MTBF", "MTTR", "信頼性"]),
    5: ("テクノロジ系", ["ローコード開発"]),
    6: ("テクノロジ系", ["SQL", "IN句", "データベース"]),
    7: ("テクノロジ系", ["回線利用率", "ネットワーク"]),
    8: ("テクノロジ系", ["HTTPS", "SSL/TLS", "ネットワーク"]),
    9: ("テクノロジ系", ["暗号の危殆化", "ハッシュ関数", "セキュリティ"]),
    10: ("テクノロジ系", ["WAF", "セキュリティ"]),
    11: ("テクノロジ系", ["E-Rモデル", "データベース"]),
    12: ("テクノロジ系", ["オブジェクト指向", "多相性", "ポリモーフィズム"]),
    13: ("マネジメント系", ["スクラム", "アジャイル", "プロダクトオーナ"]),
    14: ("マネジメント系", ["最短所要日数", "PERT図", "クリティカルパス"]),
    15: ("マネジメント系", ["情報セキュリティ監査", "物理的安全対策"]),
    16: ("ストラテジ系", ["データマイニング", "マーケットバスケット分析"]),
    17: ("ストラテジ系", ["生成AI", "オプトアウト"]),
    18: ("ストラテジ系", ["ロングテール"]),
    19: ("ストラテジ系", ["利益計算", "損益分岐"]),
    20: ("ストラテジ系", ["カーボンフットプリント", "環境"]),
}


def parse_answers() -> dict:
    """解答ファイルから {問番号: 'a'|'b'|'c'|'d'} を作る"""
    text = ANS_TXT.read_text(encoding="utf-8")
    answers = {}
    # 「問N  正解」「問 N  正解」両形式に対応
    for m in re.finditer(r"問\s*(\d+)\s+([アイウエ])", text):
        qn = int(m.group(1))
        answers[qn] = KANA_TO_ID[m.group(2)]
    return answers


def split_questions(qs_text: str) -> dict:
    """問題本文テキストを {問番号: 本文} に分割する"""
    # 改ページ文字 \f を改行に置換（問1, 3, 5, 6, 8, 11, 14, 16, 19 が \f の直後にある）
    qs_text = qs_text.replace("\f", "\n")

    # 注意事項より後ろを処理対象に
    body = qs_text.split("文意どおり解釈してください。", 1)[-1]

    # 「問N」の出現で問題を分割（問1〜問20）
    # 全角数字（１〜９）と半角数字（10〜20）の混在に対応
    blocks = {}
    # 全角→半角変換テーブル
    z2h = str.maketrans("０１２３４５６７８９", "0123456789")
    body = body.translate(z2h)

    # 「問N」は行頭または十分なインデント（半角空白2個以上）の後に出現する
    # 過去問テキストは「問N」の前にスペースまたは改行があるパターンで検出
    matches = list(re.finditer(r"(?:^|\n)\s*問\s*(\d+)\s+", body))
    for i, m in enumerate(matches):
        qn = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        block = body[start:end]
        # ページヘッダ「－ N －」を除去
        block = re.sub(r"\n\s*－\s*\d+\s*－\s*\n?", "\n", block)
        # 末尾の試験運営フッター・著作権表記・メモ用紙等を除去
        block = re.split(
            r"〔\s*メ\s*モ\s*用\s*紙\s*〕|©\s*\d{4}|試験問題に記載されている会社名",
            block,
        )[0]
        # 末尾の余分な空白を整理
        block = block.rstrip()
        blocks[qn] = block
    return blocks


def parse_question_block(block: str, qn: int) -> tuple[str, list[dict]]:
    """1問のブロックを「問題文」と「選択肢配列」に分解する。

    アプローチ：
    1. 「問N」の見出し部分を除去
    2. 「ア〜エ」の最初の出現を選択肢開始とみなす
    3. ア/イ/ウ/エ それぞれの「最初の出現位置」を取得（一度しか見ない）
    4. ブロック先頭〜ア出現直前 = 問題文、ア〜エで切る = 選択肢
    """
    full_text = block

    # 「問N」の行頭部分を取り除いて問題本文を取得
    full_text = re.sub(r"^\s*問\s*\d+\s*", "", full_text)

    # ア/イ/ウ/エの最初の出現位置をそれぞれ取得
    # マッチパターン：（行頭または空白2個以上） + カナ + （空白）
    kana_first_pos = {}
    for kana in ["ア", "イ", "ウ", "エ"]:
        # 行頭（インデント込み）か、複数空白の後に来るカナ
        pattern = re.compile(
            rf"(?:^|\n)\s+({kana})\s|\s\s+({kana})\s+",
            re.MULTILINE,
        )
        m = pattern.search(full_text)
        if m:
            # group(1) または group(2) のどちらかにマッチしている
            start = m.start(1) if m.group(1) else m.start(2)
            end = m.end(1) if m.group(1) else m.end(2)
            kana_first_pos[kana] = (start, end)

    if len(kana_first_pos) < 4:
        # 4個揃わなければエラー
        return full_text.strip(), []

    # 順序：ア < イ < ウ < エ になっている前提（出題順）
    ordered = sorted(kana_first_pos.items(), key=lambda kv: kv[1][0])

    # 問題本文 = ブロック先頭から ア の直前まで
    first_kana_start = ordered[0][1][0]
    body_text = full_text[:first_kana_start]

    # ページヘッダ等の残骸を本文から除去
    body_text = re.sub(r"\n\s*－\s*\d+\s*－\s*\n?", "\n", body_text)
    body_text = body_text.strip()

    # 各選択肢の範囲を決定
    choices = []
    for i, (kana, (start, end)) in enumerate(ordered):
        choice_start = end
        choice_end = (
            ordered[i + 1][1][0] if i + 1 < len(ordered) else len(full_text)
        )
        choice_text = full_text[choice_start:choice_end]
        # 改行・連続空白を1個の半角空白に圧縮
        choice_text = re.sub(r"\s+", " ", choice_text).strip()
        choices.append({"id": KANA_TO_ID[kana], "text": choice_text})

    return body_text, choices


def main() -> None:
    qs_text = QS_TXT.read_text(encoding="utf-8")
    answers = parse_answers()
    blocks = split_questions(qs_text)

    if len(blocks) != 20:
        print(f"⚠️ 警告: 問題数が想定と異なる ({len(blocks)})")
    if len(answers) != 20:
        print(f"⚠️ 警告: 解答数が想定と異なる ({len(answers)})")

    new_questions = []
    for qn in sorted(blocks.keys()):
        body, choices = parse_question_block(blocks[qn], qn)

        if len(choices) != 4:
            print(f"⚠️ 問{qn}: 選択肢が4つに分解できませんでした（{len(choices)}個）")
            continue

        # 図/表を含む問題は注記
        if qn in HAS_FIGURE:
            body += (
                "\n\n（注：本問題には図または表が含まれます。"
                "詳細は IPA 公開 PDF（令和7年度科目A 問"
                + str(qn)
                + "）を参照してください。）"
            )

        category, tags = QUESTION_TAGS.get(qn, ("テクノロジ系", []))

        question_id = f"FE-PAST-2025R07-A-Q{qn:02d}"
        q = {
            "question_id": question_id,
            "chapter_id": "PAST-2025r07-A",
            "category": "PAST",
            "difficulty": 2,
            "source": "past_R07_FE_A",
            "year_label": "令和7年度 公開問題（科目A）",
            "question_number": qn,
            "question_text": body,
            "choices": choices,
            "correct_answer": answers.get(qn, "a"),
            "explanation": (
                "IPA 公開問題（令和7年度 基本情報技術者試験 科目A 問"
                + str(qn)
                + "）の正解は「"
                + ["ア", "イ", "ウ", "エ"][["a", "b", "c", "d"].index(answers.get(qn, "a"))]
                + "」です。詳細な解説は IPA 公式の解答例 PDF を参照してください。"
            ),
            "related_terms": tags,
            "tags": ["過去問", "令和7年度", "科目A", category],
        }
        new_questions.append(q)

    # questions.json を更新（同 source の既存データは削除して入れ替え）
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = list(data.get("questions", []))

    # 同じ source の既存問題を一旦取り除く（再パース時の汚染データ除去）
    before = len(questions)
    questions = [q for q in questions if q.get("source") != "past_R07_FE_A"]
    removed = before - len(questions)

    # 新規追加
    questions.extend(new_questions)

    new_data = {**data, "questions": questions}
    with open(QUESTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"完了: {removed}問を入れ替え → {len(new_questions)}問追加")
    print(f"問題総数: {len(questions)}")


if __name__ == "__main__":
    main()
