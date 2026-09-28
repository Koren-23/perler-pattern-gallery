# 圖面整理相簿

拼豆圖紙參考圖的分類相簿(27 個分類、421 張)。純靜態網頁,不需要後端。

## 結構
- `index.html` 網頁本體(分類、縮圖、放大檢視)
- `images/cXX/NNN.jpg` 原圖
- `thumbs/cXX/NNN.jpg` 縮圖
- `photos.json` 分類與檔案清單(index.html 內已內嵌同一份資料)

## 本機預覽
直接雙擊 `index.html` 即可開啟。

## 新增圖片
1. 把圖放進 `images/cXX/`,同名縮圖放進 `thumbs/cXX/`
2. 在 `photos.json` 對應分類的 `files` 加上檔名,並同步更新 `index.html` 內的 `DATA`
3. `git add . && git commit -m "add images" && git push`

## 注意
圖紙多半帶有原作者浮水印,公開前請確認轉載授權。
