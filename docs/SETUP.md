# 專案安裝與設定指南

本指南將引導您如何在本地環境中設置並運行 Jotly 專案。

## 系統需求

- Python 3.10 或更高版本
- Conda (Miniconda 或 Anaconda)
- Git

## 1. 建立開發環境

我們使用 Conda 來管理虛擬環境與套件。

```bash
# 1. 進入專案目錄
cd web-bullet-journal

# 2. 建立 Conda 環境 (根據 environment.yml)
conda env create -f environment.yml

# 3. 啟動虛擬環境
conda activate bullet-journal
```

如果您更新了 `requirements.txt`，可以使用以下指令更新環境：
```bash
conda env update -f environment.yml --prune
```

## 2. 環境變數設定

專案使用環境變數來管理敏感資訊。

1. 複製範例設定檔：
   ```bash
   cp .env.example .env
   ```

2. 編輯 `.env` 檔案並填入您的設定：
   - `SECRET_KEY`: Django 安全密鑰 (已預填開發用密鑰)
   - `DEBUG`: 開發模式設為 True，正式上線請設為 False
   - `EMAIL_HOST_USER`: Gmail 帳號 (用於發送驗證信)
   - `EMAIL_HOST_PASSWORD`: Gmail 應用程式密碼

## 3. 資料庫設定

專案使用 SQLite 資料庫，需要先執行遷移 (Migrations)。

```bash
# 執行資料庫遷移
python manage.py migrate
```

## 4. 建立管理員帳號

為了登入後台管理介面，請建立一個超級使用者：

```bash
python manage.py createsuperuser
```
並依照提示輸入帳號、Email 與密碼。

## 5. 啟動開發伺服器

完成以上步驟後，即可啟動網站：

```bash
python manage.py runserver
```

打開瀏覽器前往 http://127.0.0.1:8000/ 即可看到網站首頁。

## 常見問題 (FAQ)

### Q: Email 發送失敗？
請確認您使用的是 Gmail 的「應用程式密碼」，而非您的 Google 帳戶登入密碼。且需確認 `.env` 中的設定正確。

### Q: 忘記虛擬環境名稱？
預設名稱為 `bullet-journal`。您可以使用 `conda info --envs` 查看所有環境。
