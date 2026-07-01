# AgriMind 智慧農業管理系統

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

以 AI 為核心的智慧農業管理平台，整合農場感測器數據、即時天氣、農產品價格查詢、語意知識庫與作物影像分析，透過 Claude AI 與 MCP 工具協定提供農業專屬的對話式決策輔助。

## 功能特色

- 農場儀表板與感測器數據圖表（溫濕度、降雨量、土壤 NPK）
- Claude AI 對話助手，支援 SSE 串流與圖片附件
- 即時天氣查詢（中央氣象署）與農產品批發價格查詢
- PDF / 文字知識庫上傳，pgvector 語意搜尋
- 農田影像紀錄，Claude Vision AI 分析病蟲害與土壤狀況
- Google OAuth 登入，管理員由環境變數指定

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 前端框架 | Vue 3 (Composition API) + Vite 7 |
| UI | Tailwind CSS v4 + Lucide Icons + Chart.js 4 |
| 狀態管理 | Pinia |
| 後端框架 | Python 3.12 + FastAPI + Uvicorn |
| ORM | SQLAlchemy + Alembic |
| 資料庫 | PostgreSQL 18+ + pgvector |
| AI 模型 | Claude Haiku (`claude-haiku-4-5-20251001`) |
| AI 工具協定 | MCP (fastmcp) — stdio subprocess 連線池 |
| 嵌入模型 | `paraphrase-multilingual-MiniLM-L12-v2`（384 維） |
| 身份驗證 | Google OAuth 2.0 + JWT (python-jose) |

---

## 環境需求

| 工具 | 最低版本 | 說明 |
|------|----------|------|
| Python | 3.12 | 後端 |
| uv | 最新版 | 後端套件管理 |
| Node.js | 20.19 / 22.12 | 前端 |
| PostgreSQL | 18 | 需安裝 pgvector 擴充套件 |

---

## 快速開始

### 1. 安裝前置工具

<details>
<summary>macOS</summary>

```bash
# 安裝 Homebrew（如尚未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝 PostgreSQL 18、uv、Node.js
brew install postgresql@18 uv node

# 啟動 PostgreSQL 服務
brew services start postgresql@18
```

**pgvector**：從源碼編譯安裝（官方推薦方式）：

> 版本號請至 [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) 確認最新版本再執行

```bash
export PG_CONFIG=/opt/homebrew/opt/postgresql@18/bin/pg_config
cd /tmp
git clone --branch v0.8.4 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo --preserve-env=PG_CONFIG make install
```

</details>

<details>
<summary>Windows</summary>

**PostgreSQL**：前往 [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) 下載並安裝（版本 18）

**pgvector**：需透過 Visual Studio 編譯安裝。開啟 **x64 Native Tools Command Prompt for VS**（以系統管理員身份執行）：

> 版本號請至 [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) 確認最新版本再執行

```bat
set "PGROOT=C:\Program Files\PostgreSQL\18"
cd %TEMP%
git clone --branch v0.8.4 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```

> 若尚未安裝 Visual Studio，請至 [visualstudio.microsoft.com](https://visualstudio.microsoft.com/) 下載，安裝時勾選「使用 C++ 的桌面開發」工作負載即可。

**uv**（Python 套件管理）：

```powershell
winget install --id=astral-sh.uv -e
```

**Node.js**：前往 [nodejs.org](https://nodejs.org/) 下載 LTS 版本安裝

</details>

---

### 2. 建立資料庫

<details>
<summary>macOS</summary>

Homebrew 的 `postgresql@18` 不會自動加入 PATH，需先設定：

```bash
# 將 postgresql@18 加入 PATH（執行一次即可）
echo "export PATH=\"$(brew --prefix postgresql@18)/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

Homebrew PostgreSQL 的預設超級使用者是目前的系統帳號（不是 `postgres`），請使用以下指令建立資料庫：

```bash
createdb argimind
psql argimind -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

</details>

<details>
<summary>Windows</summary>

```powershell
# 若 psql 不在 PATH，請先切換目錄：
# cd "C:\Program Files\PostgreSQL\18\bin"

psql -U postgres -c "CREATE DATABASE argimind;"
psql -U postgres -d argimind -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

</details>

---

### 3. 取得原始碼

```bash
git clone https://github.com/WenSheng31/AgriMind.git
cd AgriMind
```

---

### 4. 申請 API 金鑰

在填入 `.env` 前，需先申請以下服務的金鑰：

#### Google OAuth Client ID

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)，建立或選取一個專案
2. 建立 **OAuth 用戶端 ID**，應用程式類型選擇**網頁應用程式**
3. 在「已授權的 JavaScript 來源」加入 `http://localhost:5173`
4. 複製產生的**用戶端 ID**，填入後端 `GOOGLE_CLIENT_ID` 與前端 `VITE_GOOGLE_CLIENT_ID`

> 前後端使用**同一組** Client ID。

#### Anthropic API Key

前往 [console.anthropic.com](https://console.anthropic.com/) 建立 API Key，填入 `ANTHROPIC_API_KEY`。

#### 中央氣象署 API Key

前往 [opendata.cwa.gov.tw](https://opendata.cwa.gov.tw/) 註冊並取得 API Key，填入 `CWA_API_KEY`。

---

### 5. 後端設定

```bash
cd backend

# 安裝依賴（PyTorch 指定 CPU 版本，避免拉取 GPU 版）
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
uv pip install -r requirements.txt

# 設定環境變數（macOS / Linux）
cp .env.example .env
# Windows 請在 PowerShell 執行：
# Copy-Item .env.example .env
# 以文字編輯器開啟 .env，填入各項 API 金鑰

# 啟動服務（自動建立資料表）
uv run run.py
```

後端預設執行於 `http://localhost:8000`，互動式 API 文件：`http://localhost:8000/docs`

---

### 6. 前端設定

```bash
cd ../frontend

# 設定環境變數
cp .env.example .env
# Windows：Copy-Item .env.example .env
# 開啟 .env，將 VITE_GOOGLE_CLIENT_ID 填入與後端相同的 Client ID

npm install
npm run dev
```

前端預設執行於 `http://localhost:5173`

---

## 環境變數

在 `backend/` 目錄下建立 `.env` 檔案：

| 變數名稱 | 說明 | 範例 |
|----------|------|------|
| `DATABASE_URL` | PostgreSQL 連線字串 | `postgresql://user:pass@localhost:5432/argimind` |
| `SECRET_KEY` | JWT 簽名金鑰（請使用隨機字串，可執行 `openssl rand -hex 32` 產生） | `your_secret_key` |
| `ALGORITHM` | JWT 演算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分鐘） | `30` |
| `BACKEND_CORS_ORIGINS` | 允許的前端來源（JSON 陣列） | `["http://localhost:5173"]` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API 金鑰 | `sk-ant-...` |
| `CWA_API_KEY` | 中央氣象署開放資料平臺 API 金鑰 | `CWA-XXXXXXXX-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 用戶端 ID | `XXXXXXXXX.apps.googleusercontent.com` |
| `ADMIN_EMAILS` | 管理員 Email 清單（JSON 陣列） | `["admin@example.com"]` |
| `MCP_POOL_SIZE` | MCP subprocess 連線池大小 | `10` |

> **注意**：在 `.env` 中加入 `reload=true` 可啟用 Uvicorn 熱重載（開發用）。

---

## MCP 工具一覽

AgriMind 透過 MCP (Model Context Protocol) 為 Claude 提供 10 個農業專屬工具：

| 工具名稱 | 說明 |
|----------|------|
| `get_current_time` | 取得目前時間（ISO 格式） |
| `get_database_schema` | 回傳可查詢的資料表結構說明 |
| `query_database` | 白名單式資料庫查詢，支援聚合、時間分組、篩選 |
| `get_farms_overview` | 取得各農場最新感測數據與最近農事紀錄 |
| `get_weather` | 台灣即時天氣（中央氣象署）：觀測、7 天預報、農業天氣 |
| `get_crop_price` | 台灣農產品批發價格查詢（農業部），支援模糊比對 |
| `search_knowledge` | pgvector 語意搜尋知識庫（餘弦相似度，閾值 0.3） |
| `query_image_records` | 查詢農田影像紀錄清單 |
| `get_latest_image_per_farm` | 取得各農場最新一筆影像紀錄 |
| `analyze_image_record` | 以 Claude Vision 分析農田影像（病蟲害、土壤、管理建議） |

---

## 專案結構

```
AgriMind/
├── backend/
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # Google OAuth 登入
│   │   │   ├── agriculture.py # 農場、感測器、農事紀錄
│   │   │   ├── ai.py          # AI 查詢 / SSE 串流
│   │   │   ├── knowledge.py   # 知識庫管理
│   │   │   ├── image_records.py
│   │   │   ├── admin.py
│   │   │   ├── chat_logs.py
│   │   │   └── task_progress.py
│   │   ├── core/
│   │   │   ├── config.py      # Pydantic Settings
│   │   │   ├── database.py    # SQLAlchemy 連線池
│   │   │   ├── security.py    # JWT
│   │   │   └── init_db.py     # 啟動時建表 + pgvector
│   │   ├── models/            # SQLAlchemy 資料模型
│   │   ├── services/          # 業務邏輯層
│   │   │   ├── ai.py          # Claude + MCP 連線池管理
│   │   │   ├── embedding.py   # Sentence Transformer
│   │   │   ├── knowledge.py   # PDF 解析 + 向量儲存
│   │   │   └── image_record.py
│   │   ├── mcp_server/
│   │   │   └── server.py      # fastmcp 工具定義
│   │   └── main.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── views/             # 頁面元件
│   │   ├── components/        # 共用元件（AI 聊天、圖表、Modal）
│   │   ├── composables/       # Composition API 邏輯
│   │   ├── stores/            # Pinia 狀態管理
│   │   ├── services/          # API 呼叫層（含 SSE 解析）
│   │   └── router/            # Vue Router + 路由守衛
│   ├── public/
│   │   └── .htaccess          # Apache SPA 路由規則
│   └── package.json
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 授權

本專案採用 [MIT License](LICENSE)。
