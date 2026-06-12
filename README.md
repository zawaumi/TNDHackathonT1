# TNDHackathonT1

Muscle Galaxy は、筋トレ記録、食事、レシピ、AI生成プランを扱う Django アプリです。

## AIプランAPI

- Swagger UI: `/api/docs/`
- OpenAPI schema: `/api/schema/`
- CRUD: `/api/ai/plans/`
- 生成: `POST /api/ai/plans/generate/`
- 調整: `POST /api/ai/plans/{id}/adjust/`
- レシピ画像: `POST /api/ai/recipe-image/`
- 画面: `/ai-plan/`

## 環境変数

`.env.example` と同じ名前で `.env` を作るとローカルで読み込まれます。

```env
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=dev-only-change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,::1,0.0.0.0
DJANGO_CSRF_TRUSTED_ORIGINS=
SESSION_COOKIE_SECURE=false
CSRF_COOKIE_SECURE=false
SECURE_SSL_REDIRECT=false
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=false
SECURE_HSTS_PRELOAD=false
AI_PLANNER_MOCK_MODE=true
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
OPENAI_IMAGE_MODEL=gpt-image-2
OPENAI_ENABLE_IMAGE_GENERATION=false
OPENAI_IMAGE_GENERATION_LIMIT=4
AI_PLANNER_TIMEOUT_SECONDS=45
```

本番では `DJANGO_DEBUG=false`、推測できない `DJANGO_SECRET_KEY`、実ドメインだけの `DJANGO_ALLOWED_HOSTS` を必ず設定します。HTTPS配下で動かす場合は `SESSION_COOKIE_SECURE=true`、`CSRF_COOKIE_SECURE=true`、`SECURE_SSL_REDIRECT=true` も有効にします。HSTS preload はサブドメインを含めて HTTPS 固定できるドメインでだけ使います。

`AI_PLANNER_MOCK_MODE=true` では OpenAI API に接続せず、同じレスポンス形のモックデータを返します。本番APIを使う場合は `AI_PLANNER_MOCK_MODE=false` と `OPENAI_API_KEY` を設定します。画像生成は `OPENAI_ENABLE_IMAGE_GENERATION=true` のときだけ実行します。

## 起動

```bash
cd /Users/takutaku/workbench/TNDHackathonT1

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

すでに `.venv` がある場合は `source .venv/bin/activate` からで問題ありません。`conda` 環境と `.venv` は混ぜず、どちらか一つだけ有効にしてください。
