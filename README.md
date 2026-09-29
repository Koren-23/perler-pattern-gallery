# 拼豆圖庫

拼豆圖紙參考圖的分類相簿(31 個分類、610 張)。純靜態網頁,不需要後端。

## 結構
- `index.html` 網頁本體(分類、縮圖、放大檢視)
- `images/cXX_分類名/NNN.jpg` 原圖(例如 `images/c01_蛋仔/001.jpg`)
- `thumbs/cXX_分類名/NNN.jpg` 縮圖
- `photos.json` 分類與檔案清單(index.html 內已內嵌同一份資料)
- `tools/update_gallery.py` 同步工具(補縮圖、更新清單)

## 本機預覽
直接雙擊 `index.html` 即可開啟。

## 新增圖片
1. 把原圖放進 `images/cXX_分類名/`(檔名、格式不拘,jpg/png/webp 皆可)
2. 雙擊 `update_gallery.bat`(或執行 `python tools/update_gallery.py`),它會:
   - 把新圖改名為接續的編號 `NNN.jpg`(非 jpg 會轉成 jpg)
   - 產生對應縮圖到 `thumbs/cXX_分類名/`
   - 更新 `photos.json` 與 `index.html` 內的 `DATA`
   - 原圖被刪除的話,一併移出清單並刪除縮圖
3. `git add . && git commit -m "add images" && git push`

- 想先看看會改什麼:`python tools/update_gallery.py --dry-run`
- 換掉同名原圖時,加上 `--rebuild-thumbs` 重新產生縮圖
- 新增分類:在 `images/` 建一個新資料夾,命名為「接續編號_分類名」(例如 `c30_小熊`),執行工具後分類名稱會自動取底線後的文字;圖示預設 📁,想換可到 `photos.json` 修改 `icon` 後再執行一次工具。新分類會排在最後,想調整順序可在 `photos.json` 移動該分類的位置
- 已有的分類想改名時,資料夾名稱與 `photos.json` 的 `slug`、`name` 要一起改
- 需要 Python 3 與 Pillow(`pip install pillow`)

## 注意
圖紙多半帶有原作者浮水印,公開前請確認轉載授權。
