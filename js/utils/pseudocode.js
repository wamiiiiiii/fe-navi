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

/**
 * 疑似言語コード文字列をトレース実行可能なUIとともに描画する
 * 「次へ」ボタンで1ステップずつ進め、現在実行中の行をハイライトし、
 * その時点の変数値を表で表示する。学習者が頭の中で実行する手間を減らす。
 *
 * trace_steps は問題データ側に持たせる：
 *   trace_steps: [
 *     { line: 1, vars: { x: 0 } },
 *     { line: 2, vars: { x: 0, i: 1 } },
 *     ...
 *   ]
 *
 * @param {string} code - コード片（改行区切り）
 * @param {Array<{line: number, vars: Object}>} traceSteps - 各ステップの状態
 * @returns {HTMLElement} トレースUI付きコードブロック
 */
export function renderPseudocodeWithTrace(code, traceSteps) {
  const wrapper = createElement('div', { classes: ['pseudo-trace-wrapper'] });

  if (typeof code !== 'string' || !Array.isArray(traceSteps) || traceSteps.length === 0) {
    // 不正データの場合は通常のレンダラーにフォールバック
    wrapper.appendChild(renderPseudocode(code));
    return wrapper;
  }

  // コードブロック（行ハイライト用にDOMを保持）
  const lines = code.replace(/\n+$/, '').split('\n');
  const block = createElement('pre', {
    classes: ['pseudo-block', 'pseudo-trace-block'],
    attrs: { 'aria-label': '疑似言語コード（トレース可能）' },
  });

  const lineEls = [];
  lines.forEach((line, idx) => {
    const lineEl = createElement('span', { classes: ['pseudo-line'] });
    const num = createElement('span', {
      classes: ['pseudo-lineno'],
      text: String(idx + 1).padStart(2, ' '),
      attrs: { 'aria-hidden': 'true' },
    });
    lineEl.appendChild(num);
    const contentEl = createElement('span', { classes: ['pseudo-content'] });
    contentEl.appendChild(renderLineContent(line));
    lineEl.appendChild(contentEl);
    block.appendChild(lineEl);
    lineEls.push(lineEl);
  });
  wrapper.appendChild(block);

  // 変数表（変数名＝値の組）
  const varsBox = createElement('div', { classes: ['pseudo-trace-vars'] });
  const varsLabel = createElement('div', { classes: ['pseudo-trace-vars-label'], text: '変数の状態' });
  varsBox.appendChild(varsLabel);
  const varsTable = createElement('div', { classes: ['pseudo-trace-vars-table'] });
  varsBox.appendChild(varsTable);
  wrapper.appendChild(varsBox);

  // 操作ボタン
  const ctrls = createElement('div', { classes: ['pseudo-trace-ctrls'] });
  const stepLabel = createElement('span', { classes: ['pseudo-trace-step-label'], text: '' });
  const prevBtn = createElement('button', { classes: ['pseudo-trace-btn'], text: '← 前へ' });
  const nextBtn = createElement('button', { classes: ['pseudo-trace-btn', 'pseudo-trace-btn-primary'], text: '次へ →' });
  const resetBtn = createElement('button', { classes: ['pseudo-trace-btn'], text: '⟲ 最初から' });
  ctrls.appendChild(prevBtn);
  ctrls.appendChild(nextBtn);
  ctrls.appendChild(resetBtn);
  ctrls.appendChild(stepLabel);
  wrapper.appendChild(ctrls);

  // 内部状態：現在のステップindex（0始まり）
  let currentStep = 0;

  function applyStep(idx) {
    // ハイライト解除
    lineEls.forEach((el) => el.classList.remove('pseudo-line--active'));

    const step = traceSteps[idx];
    if (!step) return;

    // 該当行をハイライト（line は 1始まり）
    const lineIdx = (step.line || 1) - 1;
    if (lineEls[lineIdx]) {
      lineEls[lineIdx].classList.add('pseudo-line--active');
    }

    // 変数表を更新（イミュータブルに作り直す）
    varsTable.innerHTML = '';
    const vars = step.vars || {};
    if (Object.keys(vars).length === 0) {
      varsTable.appendChild(createElement('div', { classes: ['pseudo-trace-vars-empty'], text: '（変数なし）' }));
    } else {
      Object.entries(vars).forEach(([k, v]) => {
        const row = createElement('div', { classes: ['pseudo-trace-var-row'] });
        row.appendChild(createElement('span', { classes: ['pseudo-trace-var-name'], text: k }));
        row.appendChild(createElement('span', { classes: ['pseudo-trace-var-eq'], text: '=' }));
        row.appendChild(createElement('span', { classes: ['pseudo-trace-var-value'], text: formatValue(v) }));
        varsTable.appendChild(row);
      });
    }

    // ステップ表示・ボタン状態
    stepLabel.textContent = `ステップ ${idx + 1} / ${traceSteps.length}`;
    prevBtn.disabled = idx <= 0;
    nextBtn.disabled = idx >= traceSteps.length - 1;
  }

  prevBtn.addEventListener('click', () => {
    if (currentStep > 0) {
      currentStep--;
      applyStep(currentStep);
    }
  });
  nextBtn.addEventListener('click', () => {
    if (currentStep < traceSteps.length - 1) {
      currentStep++;
      applyStep(currentStep);
    }
  });
  resetBtn.addEventListener('click', () => {
    currentStep = 0;
    applyStep(currentStep);
  });

  // 初期状態を適用
  applyStep(0);

  return wrapper;
}

/**
 * 変数値を表示用の文字列に整形する（オブジェクト・配列・null も読みやすく）
 */
function formatValue(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return '[' + v.map(formatValue).join(', ') + ']';
  if (typeof v === 'object') {
    return '{' + Object.entries(v).map(([k, val]) => `${k}: ${formatValue(val)}`).join(', ') + '}';
  }
  if (typeof v === 'string') return JSON.stringify(v);
  return String(v);
}
