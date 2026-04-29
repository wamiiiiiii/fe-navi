/**
 * pseudocode.js
 * IPA 基本情報技術者試験 科目B の疑似言語コードを描画するユーティリティ。
 *
 * IPA 疑似言語の主な記号：
 *   ◆  条件分岐（if）／繰返しの終端マーカー
 *   ▲  繰返し処理（while / for）
 *   ■  プログラム・関数の定義
 *   ←  代入演算子
 *
 * Phase 2 ではコード片を「等幅フォント・行番号・記号着色」で表示するだけ。
 * Phase 3 で変数トレース／ステップ実行 UI を追加する想定。
 */

import { createElement } from './render.js';

/**
 * 行頭の記号や予約語に CSS クラスを割り当てるための走査ルール
 * シンプルな先頭マッチ。完全な構文解析はしない（学習用途では十分）
 */
const SYMBOL_CLASSES = {
  '◆': 'pseudo-sym-cond',
  '▲': 'pseudo-sym-loop',
  '■': 'pseudo-sym-def',
};

/**
 * 単一行をスパン化する。記号は色分けし、それ以外はそのまま表示する。
 * @param {string} line - 1行分のテキスト
 * @returns {DocumentFragment} 着色済みノード列
 */
function renderLineContent(line) {
  const frag = document.createDocumentFragment();
  if (!line) {
    frag.appendChild(document.createTextNode(''));
    return frag;
  }

  // 行頭の空白（インデント）を保持して別ノードに切り出す
  const indentMatch = line.match(/^(\s*)(.*)$/);
  const indent = indentMatch[1] || '';
  const rest = indentMatch[2] || '';

  if (indent) {
    const indentEl = createElement('span', { classes: ['pseudo-indent'], text: indent });
    frag.appendChild(indentEl);
  }

  if (!rest) {
    return frag;
  }

  // 行頭の特殊記号（◆▲■）を着色して切り出す
  const firstChar = rest.charAt(0);
  if (SYMBOL_CLASSES[firstChar]) {
    const symEl = createElement('span', {
      classes: ['pseudo-symbol', SYMBOL_CLASSES[firstChar]],
      text: firstChar,
    });
    frag.appendChild(symEl);

    // 残り（記号の後ろの式）はテキストのまま
    const after = rest.slice(1);
    if (after) {
      frag.appendChild(document.createTextNode(after));
    }
  } else {
    // 通常の処理行：代入演算子「←」だけ強調する
    const arrowIdx = rest.indexOf('←');
    if (arrowIdx >= 0) {
      const left = rest.slice(0, arrowIdx);
      const right = rest.slice(arrowIdx + 1);
      if (left) frag.appendChild(document.createTextNode(left));
      const arrowEl = createElement('span', {
        classes: ['pseudo-arrow'],
        text: '←',
      });
      frag.appendChild(arrowEl);
      if (right) frag.appendChild(document.createTextNode(right));
    } else {
      frag.appendChild(document.createTextNode(rest));
    }
  }

  return frag;
}

/**
 * 疑似言語コード文字列をDOMにレンダリングする
 * 改行で分割し、行番号付きでブロックを構築する
 *
 * @param {string} code - コード片（改行区切り）
 * @param {Object} [options]
 * @param {boolean} [options.showLineNumbers=true] - 行番号を表示するか
 * @returns {HTMLElement} 描画済みのコードブロック
 */
export function renderPseudocode(code, options = {}) {
  const { showLineNumbers = true } = options;

  const container = createElement('pre', {
    classes: ['pseudo-block'],
    attrs: { 'aria-label': '疑似言語コード' },
  });

  if (typeof code !== 'string' || code.length === 0) {
    container.appendChild(document.createTextNode(''));
    return container;
  }

  // 末尾の余計な改行を取り除いてから分割する（行末の空行で行番号がずれるのを防ぐ）
  const lines = code.replace(/\n+$/, '').split('\n');

  lines.forEach((line, idx) => {
    const lineEl = createElement('span', { classes: ['pseudo-line'] });

    if (showLineNumbers) {
      const num = createElement('span', {
        classes: ['pseudo-lineno'],
        text: String(idx + 1).padStart(2, ' '),
        attrs: { 'aria-hidden': 'true' },
      });
      lineEl.appendChild(num);
    }

    const contentEl = createElement('span', { classes: ['pseudo-content'] });
    contentEl.appendChild(renderLineContent(line));
    lineEl.appendChild(contentEl);

    container.appendChild(lineEl);
  });

  return container;
}
