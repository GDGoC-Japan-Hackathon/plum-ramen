# uMeDiary

> u = あなた / Me = 私 / **uMe = 梅** / Diary = 日記
> **あなた自身を深く知るための日記アプリ**

---

## コンセプト

「日記を書くことで、自分自身を知る。知ったうえで新たな行動を促し、自分とは何なのかを考える仕組みを」

日記 × 16タイプ性格診断の Web アプリ。

既存の16タイプ診断は「一度やって終わり」になりがち。でも人の性格は日によって揺れる。だからこそ、日記という日常の積み重ねを通じて「今日の自分」をAIが継続的に分析し、自己理解を深めるきっかけを与えたい。

---

## アプリの流れ

```
1. 日記を書く        → 今日あったことや感情を自由記述
2. AI が質問を生成   → 日記の内容に基づき、性格判定に必要な追加質問を自動生成
                        （汎用的な質問ではなく、その日の具体的な場面に紐づいた質問）
3. 質問に回答        → 3択形式で回答
4. 診断結果を表示   → 性格タイプ・4軸スコア・要約・今後のヒントを表示
```

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | Jinja2テンプレート + Vanilla JS |
| バックエンド | FastAPI (Python) |
| AI | Gemini 2.5 Flash (Vertex AI) — ユング理論の4軸（I/E, N/S, T/F, J/P）をプロンプトで制御し構造化JSONで返す |
| 認証 | Firebase Authentication (Google ログイン) |
| DB | Google Cloud SQL (PostgreSQL) |
| インフラ | Cloud Run (サーバーレスコンテナ) |
| CI/CD | GitHub Actions — push → ビルド → Artifact Registry → Cloud Run 自動デプロイ |

### インフラ構成と役割

```
GitHub Actions
    │ push
    ▼
Artifact Registry   ← Docker イメージ管理
    │ deploy
    ▼
Cloud Run           ← FastAPI アプリ実行（サーバーレス）
    ├── Firebase Auth  ← Bearer トークン検証・ユーザーID変換
    ├── Vertex AI      ← 質問生成・性格診断の推論
    └── Cloud SQL      ← 日記・質問・回答・診断結果の永続化
```

---

## ディレクトリ構成

```
plum-ramen/
├── app.py              # FastAPI エントリポイント・ルーター登録
├── core/               # 横断的な基盤（DB接続・認証・Geminiクライアント）
│   ├── auth.py         #   Firebase トークン検証 → user_id に変換
│   ├── db.py           #   Cloud SQL Connector 経由で PostgreSQL に接続
│   └── gemini.py       #   Vertex AI の Gemini クライアント（シングルトン）
├── api/routers/        # REST API エンドポイント定義
│   ├── diaries.py      #   日記の保存・取得
│   ├── questions.py    #   AI による質問生成・保存
│   ├── answers.py      #   回答の保存
│   └── result.py       #   診断結果の生成・保存・取得
├── services/           # ビジネスロジック（AI 呼び出し・DB 操作）
├── schemas/            # リクエスト/レスポンスの型定義（Pydantic）
├── prompts/            # Gemini に渡すプロンプト（質問生成・診断生成）
├── web/routers/        # HTML ページのルーティング (SSR)
├── templates/          # Jinja2 HTML テンプレート
│   ├── login.html
│   ├── diary_list.html
│   ├── diary_form.html
│   ├── answer_questions.html
│   ├── generate_loading.html
│   └── display_result.html
├── static/             # JS・CSS（Firebase 認証処理含む）
├── .github/workflows/  # CI/CD パイプライン
├── Dockerfile
└── requirements.txt
```

---


## 今後の展望

「積み重ねで自己理解を深める」というコンセプトを完成させるため、以下の順番で拡張していく。

### Phase 1 — 週サマリー × 時系列グラフ（セットでリリース）

複数の診断結果をAIが週単位で統合し「今週のあなたは〇〇な傾向でした」と要約する。
同時に4軸スコア（E/I, N/S, T/F, J/P）の時系列折れ線グラフを表示し、性格の「揺れ」を数字で可視化する。
「性格は一つに定まらない」というコンセプトをデータで証明できる機能。

```
E/I軸
E +100 |
       |    *
    0  |  *   *       *
       |        *   *
I -100 |          *
       +---+---+---+---+--→ 日付
```

### Phase 2 — 日記キーワードと性格傾向の相関

頻出ワード（「仕事」「友人」「疲れた」など）と4軸スコアの関係をヒートマップで表示。
「仕事の話を書いた日はT（論理型）が上がる」といった自己発見を促す。
データが蓄積されてから意味が出る機能なので、継続利用者向けに追加。

### Phase 3 — 他ユーザーとの匿名比較

「月曜日はI（内向き）が多い」「雨の日はF（感情型）が増える」といった集合知の提供。
個人の自己理解を超えて「人間ってこういうもの」という発見につなげる。
ユーザー数が必要なため、プロダクトが成熟してから実装する。

---

## 素材クレジット

- 生成結果のロード画面の背景テクスチャ「Natural Paper」は Mihaela Hinayon による作品です。Transparent Textures 経由で利用し、出典は Subtle Patterns、ライセンスは CC BY-SA 3.0 

---

## チーム

ハッカソンチーム: 梅ラーメン
