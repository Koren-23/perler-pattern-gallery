# 圖面整理相簿

拼豆圖紙參考圖的分類相簿(27 個分類、421 張)。純靜態網頁,不需要後端。

## 結構
- `index.html` 網頁本體(分類、縮圖、放大檢視)
- `images/cXX/NNN.jpg` 原圖
- `thumbs/cXX/NNN.jpg` 縮圖
- `photos.json` 分類與檔案清單(index.html 內已內嵌同一份資料)
- `tools/update_gallery.py` 同步工具(補縮圖、更新清單)

## 本機預覽
直接雙擊 `index.html` 即可開啟。

## 新增圖片
1. 把原圖放進 `images/cXX/`(檔名、格式不拘,jpg/png/webp 皆可)
2. 雙擊 `update_gallery.bat`(或執行 `python tools/update_gallery.py`),它會:
   - 把新圖改名為接續的編號 `NNN.jpg`(非 jpg 會轉成 jpg)
   - 產生對應縮圖到 `thumbs/cXX/`
   - 更新 `photos.json` 與 `index.html` 內的 `DATA`
   - 原圖被刪除的話,一併移出清單並刪除縮圖
3. `git add . && git commit -m "add images" && git push`

- 想先看看會改什麼:`python tools/update_gallery.py --dry-run`
- 換掉同名原圖時,加上 `--rebuild-thumbs` 重新產生縮圖
- 新增分類:在 `images/` 建一個新資料夾(例如 `c28`),執行工具後到 `photos.json` 修改該分類的 `name` 與 `icon`,再執行一次工具
- 需要 Python 3 與 Pillow(`pip install pillow`)

## 注意
圖紙多半帶有原作者浮水印,公開前請確認轉載授權。
