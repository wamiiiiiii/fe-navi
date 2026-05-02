/**
 * sw.js
 * Service Worker - オフラインキャッシュ管理
 *
 * キャッシュ戦略：
 * - UIリソース（HTML・CSS・JS）: Stale-While-Revalidate（キャッシュを返しつつバックグラウンドで更新）
 * - JSONデータファイル: Cache First（キャッシュ優先・オフライン対応）
 * - その他: Network First（ネットワーク優先）
 */

// キャッシュの名前（バージョンを上げると古いキャッシュを削除できる）
// 【重要・運用ルール】リリース時はこの値と index.html の <meta name="app-version"> を必ず一緒に更新する。
// 設定画面のバージョン表示が app-version から動的に読まれるため、ユーザーが現在どの版を見ているかを
// 判別できるようになる。SW のキャッシュバンプを忘れると古いデータが配信され続けるので注意。
//
// v1 (app-version 0.1.0): iPass-navi をベースに FE ナビ用にリブランドした初版。
//   ストレージキー fe_*、SW キャッシュ fe-navi-*、アプリ名 FE ナビ。
//   問題データ・教科書・用語辞書は空（科目A/B のスケルトン構造のみ）。
// v2 (app-version 0.2.0): Phase 1着手。シラバス Ver.9.0 の章構造（22章）展開・
//   科目A サンプル問題 10 問・用語 12 件追加。
// v3 (app-version 0.3.0): Phase 2 — 疑似言語コードレンダラー実装。
//   utils/pseudocode.js + css/pseudocode.css。
//   科目B サンプル問題 4 問追加（プログラミング 3・情報セキュリティ 1）。
// v4 (app-version 0.4.0): Phase C — シラバス Ver.9.0 全節タイトル展開（29章×235節）。
//   各節は body/keywords/summary_points が空のスケルトン。教科書本文は Phase A で投入予定。
// v5 (app-version 0.5.0): Phase B — 科目A 4択問題 230問追加（既存14問→244問）。
//   並列 Sonnet 6本で生成。23章をすべて 6〜14 問でカバー、正解分布ほぼ均等。
// v6 (app-version 0.6.0): Phase A — 教科書本文（body/keywords/summary_points）生成。
//   試走 A-tech-01 + 並列9エージェント（Sonnet 5・Haiku 4）で 28章225節を一括生成。
//   全235節 body 平均452字 / keywords 4〜6個 / summary_points 3点を完備。
// v7 (app-version 0.6.1): iPass v1.7.1〜1.7.3 で発覚・修正したバグ4件を FE ナビにも反映。
//   1) mobile-safari の設定タブ遷移バグ：home/textbook/glossary の async 描画完了直前に
//      getCurrentRoute() ガードを追加し、レース時に古い描画を破棄。
//   2) 辞書スクロール時の50音インデックスのズレ：検索バーとフィルターバーを
//      .glossary-sticky-header 親に集約し、検索バー高さに依存しない一体追従に変更。
//   3) 損益分岐点等 timeline型図解の文字被り：annotation を絶対配置の同一行から
//      縦並び（display:block + position:relative）に変更し、長文も折り返して重ならないように。
//   4) 用語辞書の50音順ソート：rowOrder で表示順固定、各グループ内も localeCompare('ja') ソート。
// v8 (app-version 0.7.0): 科目B 4択問題を 4問 → 70問に大幅拡充（Phase D）。
//   並列5エージェント（Sonnet）+ 試走1エージェントで6章を分担生成。
//   - B-sec-01 (12問・情報セキュリティ基本)
//   - B-sec-02 (10問・情報セキュリティ管理)
//   - B-prog-01 (12問・プログラミング基礎・pseudocode 7問)
//   - B-prog-02 (14問・アルゴリズムとデータ構造・pseudocode 9問)
//   - B-prog-03 (12問・処理形態と関数・pseudocode 7問)
//   - B-prog-04 (10問・テスト・保守・pseudocode 5問)
//   pseudocode 付き総数 28問。explanation 平均 189字。正解分布 a=21/b=17/c=17/d=15。
//   既存サンプル4問（章単位粒度）は新形式（節単位粒度）と入れ替え。
// v9 (app-version 0.7.1): PWA アイコンを iPass 流用から FE 専用に差し替え。
//   icon-192.png / icon-512.png / favicon.png を Pillow で生成（テーマカラー
//   #2d3561 + 白文字「FE」のシンプルロゴ）。ホーム画面に追加した時のアイコンが
//   iPass ナビと混在する問題を解消。
// v10 (app-version 0.8.0): 科目A マネジメント系 3章を節5問体制に到達（Phase E-1）。
//   並列3エージェント（章ごと分担・各 17〜27問）で 66問追加。
//   - A-mgmt-01 (プロジェクトマネジメント): 既存9 → 36問（節5×7 + 章単位1）
//   - A-mgmt-02 (サービスマネジメント): 既存8 → 30問（節5×6）
//   - A-mgmt-03 (システム監査): 既存8 → 25問（節5×5）
//   マネジメント系18節すべてが 5問以上達成。explanation 平均168字。
//   正解分布 a=17/b=16/c=17/d=16、難易度 1=15/2=34/3=17。
//   total questions: 310 → 376問。
// v11 (app-version 0.9.0): 科目A ストラテジ系 7章を節5問体制に到達（Phase E-2）。
//   並列7エージェント（章ごと分担）で 207問追加。
//   - A-strat-01 (経営戦略・7節): +29問
//   - A-strat-02 (システム戦略・6節): +24問
//   - A-strat-03 (経営管理・7節): +29問
//   - A-strat-04 (技術戦略・5節): +19問
//   - A-strat-05 (応用システム・7節): +29問
//   - A-strat-06 (経営財務・9節): +36問
//   - A-strat-07 (法務・10節): +41問
//   ストラテジ系51節すべてが 5問以上達成。explanation 平均149字。
//   正解分布 a=51/b=52/c=53/d=51（理想的均等）、難易度 1=60/2=93/3=54。
//   total questions: 376 → 583問（科目A 513 + 科目B 70）。
const CACHE_NAME = 'fe-navi-v11';
const DATA_CACHE_NAME = 'fe-navi-data-v11';

// アプリシェル（UIリソース）：初回インストール時にキャッシュするファイルリスト
const APP_SHELL_FILES = [
  './',
  './index.html',
  './manifest.json',
  './css/reset.css',
  './css/variables.css',
  './css/layout.css',
  './css/home.css',
  './css/textbook.css',
  './css/quiz.css',
  './css/glossary.css',
  './css/settings.css',
  './css/diagram.css',
  './css/celebration.css',
  './css/pseudocode.css',
  './js/app.js',
  './js/router.js',
  './js/store.js',
  './js/dataLoader.js',
  './js/screens/home.js',
  './js/screens/textbook.js',
  './js/screens/quiz.js',
  './js/screens/glossary.js',
  './js/screens/settings.js',
  './js/utils/render.js',
  './js/utils/progress.js',
  './js/utils/diagram.js',
  './js/utils/srs.js',
  './js/utils/celebration.js',
  './js/utils/pseudocode.js',
  './favicon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// JSONデータファイル：Cache First で管理するファイル
// loadQuestions() が並行fetchで統合するため、追加した questions*.json も含める想定
const DATA_FILES = [
  './data/chapters.json',
  './data/questions.json',
  './data/glossary.json',
  './data/diagrams.json',
];

// ===================================================
// インストールイベント：初回キャッシュの構築
// ===================================================
self.addEventListener('install', (event) => {
  console.info('[SW] インストール中...');

  event.waitUntil(
    (async () => {
      // アプリシェルを個別にキャッシュする（1ファイル失敗しても他は続行する）
      const appCache = await caches.open(CACHE_NAME);
      const appResults = await Promise.allSettled(
        APP_SHELL_FILES.map((file) => appCache.add(file))
      );
      const appFailed = appResults.filter((r) => r.status === 'rejected');
      if (appFailed.length > 0) {
        console.warn(`[SW] アプリシェルのキャッシュに${appFailed.length}件失敗しました:`, appFailed);
      } else {
        console.info('[SW] アプリシェルのキャッシュが完了しました');
      }

      // データファイルを個別にキャッシュする（1ファイル失敗しても他は続行する）
      const dataCache = await caches.open(DATA_CACHE_NAME);
      const dataResults = await Promise.allSettled(
        DATA_FILES.map((file) => dataCache.add(file))
      );
      const dataFailed = dataResults.filter((r) => r.status === 'rejected');
      if (dataFailed.length > 0) {
        console.warn(`[SW] データファイルのキャッシュに${dataFailed.length}件失敗しました（後でフェッチします）:`, dataFailed);
      } else {
        console.info('[SW] データファイルのキャッシュが完了しました');
      }

      // インストール直後に有効化する（activate待ちをスキップ）
      await self.skipWaiting();
    })()
  );
});

// ===================================================
// アクティベートイベント：古いキャッシュの削除
// ===================================================
self.addEventListener('activate', (event) => {
  console.info('[SW] アクティブ化中...');

  event.waitUntil(
    (async () => {
      // 現在のバージョン以外のキャッシュをすべて削除する
      const cacheNames = await caches.keys();
      const deletions = cacheNames
        .filter((name) => name !== CACHE_NAME && name !== DATA_CACHE_NAME)
        .map((name) => {
          console.info('[SW] 古いキャッシュを削除します:', name);
          return caches.delete(name);
        });

      await Promise.all(deletions);

      // すぐにページの制御を開始する
      await self.clients.claim();

      console.info('[SW] アクティブ化完了');
    })()
  );
});

// ===================================================
// フェッチイベント：リクエストの横取りとキャッシュ処理
// ===================================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // GETリクエスト以外はService Workerが処理しない
  if (request.method !== 'GET') {
    return;
  }

  // 外部ドメインのリクエストはそのまま通す
  if (url.origin !== location.origin) {
    return;
  }

  // JSONデータファイルは「Cache First」戦略
  if (DATA_FILES.some((file) => url.pathname.endsWith(file.slice(1)))) {
    event.respondWith(cacheFirstStrategy(request, DATA_CACHE_NAME));
    return;
  }

  // UIリソースは「Stale-While-Revalidate」戦略
  event.respondWith(staleWhileRevalidateStrategy(request, CACHE_NAME));
});

// ===================================================
// キャッシュ戦略の実装
// ===================================================

/**
 * Cache First 戦略
 * キャッシュがあればキャッシュから返す。なければネットワークから取得してキャッシュする。
 * データファイル向け（JSONは頻繁に変わらないため）
 * @param {Request} request - フェッチリクエスト
 * @param {string} cacheName - 使用するキャッシュ名
 * @returns {Promise<Response>} レスポンス
 */
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    // ignoreSearch: true でクエリパラメータを無視してキャッシュを検索する
    const cached = await cache.match(request, { ignoreSearch: true });

    if (cached) {
      // キャッシュヒット：キャッシュからレスポンスを返す
      return cached;
    }

    // キャッシュミス：ネットワークから取得してキャッシュに保存
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // レスポンスのクローンを作成してキャッシュに保存（ストリームは一度しか読めないため）
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;

  } catch (error) {
    // ネットワークエラー：オフラインフォールバック
    console.warn('[SW] ネットワークエラー（Cache First）:', request.url);
    return new Response(
      JSON.stringify({ error: 'オフラインのため、データを取得できませんでした' }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}

/**
 * Stale-While-Revalidate 戦略
 * キャッシュがあればすぐに返しつつ、バックグラウンドでキャッシュを更新する。
 * UIリソース向け（高速表示を優先しつつ最新版を取得）
 * @param {Request} request - フェッチリクエスト
 * @param {string} cacheName - 使用するキャッシュ名
 * @returns {Promise<Response>} レスポンス
 */
async function staleWhileRevalidateStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  // ignoreSearch: true でクエリパラメータを無視してキャッシュを検索する
  const cached = await cache.match(request, { ignoreSearch: true });

  // バックグラウンドでキャッシュを更新するPromise（awaitしない）
  const networkPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => {
    // ネットワークエラーはログに残すだけ（バックグラウンドなのでユーザーに影響しない）
    // キャッシュミス時にawaitされる可能性があるためnullを返す（undefinedを防止）
    console.warn('[SW] バックグラウンド更新に失敗しました:', request.url);
    return null;
  });

  if (cached) {
    // キャッシュがあれば即座に返す（バックグラウンドで更新は続行）
    return cached;
  }

  // キャッシュがなければネットワークからの応答を待つ
  try {
    const response = await networkPromise;
    return response || new Response('', { status: 404 });
  } catch (error) {
    // オフラインかつキャッシュなし：エラーページを返す
    return new Response(
      `<!DOCTYPE html>
      <html lang="ja">
      <head><meta charset="UTF-8"><title>オフライン</title></head>
      <body>
        <h1>オフラインです</h1>
        <p>インターネット接続を確認してください。</p>
        <p>一度アプリを読み込んだ後はオフラインでも使用できます。</p>
      </body>
      </html>`,
      {
        status: 200,
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      }
    );
  }
}
