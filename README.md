# 拼豆圖庫

拼豆圖紙參考圖的分類相簿(44 個分類、988 張)。純靜態網頁,不需要後端。

## 結構
- `index.html` 網頁本體(分類、縮圖、放大檢視)
- `images/cXX_分類名/cXX_NNN.jpg` 原圖(例如 `images/c01_蛋仔/c01_001.jpg`,檔名前綴 = 資料夾編號)
- `thumbs/cXX_分類名/cXX_NNN.jpg` 縮圖
- `photos.json` 分類與檔案清單(index.html 內已內嵌同一份資料)
- `tools/update_gallery.py` 同步工具(補縮圖、更新清單)

## 本機預覽
直接雙擊 `index.html` 即可開啟。

## 新增圖片
1. 把原圖放進 `images/cXX_分類名/`(檔名、格式不拘,jpg/png/webp 皆可)
2. 雙擊 `update_gallery.bat`(或執行 `python tools/update_gallery.py`),它會:
   - 先從 GitHub 取得最新內容(包含手機上傳的圖片),避免編號衝突
   - 把新圖改名為接續的編號 `cXX_NNN.jpg`(非 jpg 會轉成 jpg)
   - 產生對應縮圖到 `thumbs/cXX_分類名/`
   - 更新 `photos.json` 與 `index.html` 內的 `DATA`
   - 原圖被刪除的話,一併移出清單並刪除縮圖
3. `git add . && git commit -m "add images" && git push`

- 想先看看會改什麼:`python tools/update_gallery.py --dry-run`
- 換掉同名原圖時,加上 `--rebuild-thumbs` 重新產生縮圖
- 新增分類:在 `images/` 建一個新資料夾,命名為「接續編號_分類名」(例如 `c30_小熊`),執行工具後分類名稱會自動取底線後的文字;圖示預設 📁,想換可到 `photos.json` 修改 `icon` 後再執行一次工具。新分類會排在最後,想調整順序可在 `photos.json` 移動該分類的位置
- 密碼分類:在 `photos.json` 該分類加上 `"locked": true` 與 `"pwHash"`(密碼的 SHA-256,每個分類可不同,例如 `python -c "import hashlib;print(hashlib.sha256(b'密碼').hexdigest())"`)。注意這只是網頁上的門檻,圖片本身仍公開在 repo 中,短密碼也很容易被試出來
- 固定排最後:分類加上 `"pinLast": true`(目前是 CINDY、TIMOTHY);新分類會自動排在它們前面
- 防止下載:網頁關閉了長按「儲存到照片」、右鍵「另存圖片」與拖曳存檔。截圖或直接從 GitHub repo 下載仍無法阻止
- 分類頁加參考連結:在 `photos.json` 該分類加上 `"links": [{"name": "顯示名稱", "url": "網址"}]`,再執行一次工具
- 搬移照片到別的分類:直接把原圖(例如 `c27_060.jpg`)從一個資料夾拖到另一個,再執行工具。因為檔名帶有資料夾編號,不會覆蓋到目的地的照片;工具會把它改成目的地的下一個編號,並更新兩邊的清單與縮圖。只需搬 `images/` 裡的原圖,`thumbs/` 不用動
- 首頁分類圖示會用該分類第一張照片;沒有照片、密碼分類,或在 `photos.json` 標了 `"emojiIcon": true` 的分類(目前是「其他」)則顯示 `icon` 表情符號
- 已有的分類想改名時,資料夾名稱與 `photos.json` 的 `slug`、`name` 要一起改
- 需要 Python 3 與 Pillow(`pip install pillow`)

## 拼豆圖紙產生器
`generator.html`(首頁上方有按鈕):選一張照片,設定寬高(顆)與顏色數量,自動產生附色號與每 10 格粗線的圖紙,以及每個顏色需要幾顆。可選擇去除背景。照片只在裝置上處理,不會上傳。色號是該圖紙自己的編號,不對應特定品牌。

## 手機上傳(iPhone)
網址:https://koren-23.github.io/perler-pattern-gallery/upload.html
(建議用 Safari 開啟後,按「分享 → 加入主畫面」,之後就像 App 一樣點開)

選分類 → 選擇照片加入清單;可以換分類再選照片,累積好幾個分類 → 按一次「上傳全部」。清單中每張照片可按 ✕ 移除;分類選錯時點該組上方的分類名稱即可整組改分類;「清除全部」清空清單,上傳中可按「取消上傳」(存檔前取消,網站不會有任何變更)。網頁會自動縮小照片、產生縮圖、更新清單並存進 GitHub,約 1 分鐘後出現在圖庫。HEIC 會自動轉成 JPG。

第一次使用需要貼上 GitHub 權杖(只存在那支手機,不會上傳):
1. 登入 GitHub → 右上角頭像 → Settings → 左側最下方 Developer settings
2. Personal access tokens → Fine-grained tokens → Generate new token
3. Token name 隨意(例如「手機上傳」);Expiration 選想要的期限
4. Repository access 選 Only select repositories → `perler-pattern-gallery`
5. Permissions → Repository permissions → Contents 設為 **Read and write**
6. Generate token,複製 `github_pat_` 開頭的那串,貼到上傳頁

也可以在上傳頁按「＋ 新增分類」,輸入名稱(與可選的圖示)直接建立新分類,會排在最後。

權杖過期或手機遺失時,到同一頁刪除(Revoke)舊權杖再產生新的即可。改分類名稱、調整順序、刪除圖片、密碼等仍需在電腦上處理。

### 電腦自動同步手機上傳的圖片
`tools/auto_sync.ps1` 會執行 `git pull --ff-only`(只下載,不上傳、不覆蓋本機未版控的檔案),紀錄寫在 `%LOCALAPPDATA%\perler-gallery-sync.log`。可用 Windows「工作排程器」設定每天執行;沒設定的話,雙擊 `update_gallery.bat` 也會先同步。

## 注意
圖紙多半帶有原作者浮水印,公開前請確認轉載授權。
