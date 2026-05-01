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
const CACHE_NAME = 'fe-navi-v6';
const DATA_CACHE_NAME = 'fe-navi-data-v6';

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
