"""同步相簿:掃描 images/,補縮圖,並更新 photos.json 與 index.html 內的 DATA。

用法:把新圖放進 images/cXX/ 之後執行
    python tools/update_gallery.py
加上 --dry-run 只列出會做的事,不實際修改;
換掉同名原圖時加上 --rebuild-thumbs 重新產生所有縮圖。
執行前會先 git pull 取得手機上傳的圖片(--no-pull 可略過)。
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
THUMBS = ROOT / "thumbs"
PHOTOS_JSON = ROOT / "photos.json"
INDEX_HTML = ROOT / "index.html"

THUMB_BOX = (300, 300)
THUMB_QUALITY = 80
CONVERT_QUALITY = 92
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
STANDARD_NAME = re.compile(r"^\d{3}\.jpg$")
DATA_LINE = re.compile(r"^var DATA=.*;$", re.MULTILINE)
CATEGORY_PREFIX = re.compile(r"^c\d+_")


def next_number(folder):
    nums = [int(p.stem) for p in folder.glob("*.jpg") if STANDARD_NAME.match(p.name)]
    return max(nums, default=0) + 1


def normalize_names(folder, dry_run, log):
    """把非 NNN.jpg 的新圖改名(必要時轉成 jpg),接在現有編號後面。"""
    others = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS and not STANDARD_NAME.match(p.name)
    )
    n = next_number(folder)
    for src in others:
        dst = folder / f"{n:03d}.jpg"
        n += 1
        if src.suffix.lower() in (".jpg", ".jpeg"):
            log(f"  改名 {src.name} -> {dst.name}")
            if not dry_run:
                src.rename(dst)
        else:
            log(f"  轉檔 {src.name} -> {dst.name}")
            if not dry_run:
                with Image.open(src) as im:
                    im = ImageOps.exif_transpose(im)
                    if im.mode in ("RGBA", "LA", "P"):
                        im = im.convert("RGBA")
                        bg = Image.new("RGB", im.size, (255, 255, 255))
                        bg.paste(im, mask=im.getchannel("A"))
                        im = bg
                    im.convert("RGB").save(dst, "JPEG", quality=CONVERT_QUALITY)
                src.unlink()


def make_thumb(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail(THUMB_BOX, Image.LANCZOS)
        im.save(dst, "JPEG", quality=THUMB_QUALITY, optimize=True)


def pull_latest(log):
    """先拿到手機上傳的新圖,避免本機和手機各自用了同一個編號。"""
    log("從 GitHub 取得最新內容(包含手機上傳的圖片)…")
    try:
        r = subprocess.run(["git", "pull", "--ff-only"], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        log("[注意] 找不到 git,略過同步。\n")
        return
    if r.returncode == 0:
        log(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "已是最新")
        log("")
    else:
        log("[注意] 無法自動同步 GitHub 上的最新內容,圖片仍會繼續處理。")
        log("       版控前請告訴 Claude「有同步失敗」,以免編號衝突。")
        log("       " + (r.stderr.strip().splitlines() or [""])[-1] + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="只列出變更,不修改任何檔案")
    ap.add_argument("--rebuild-thumbs", action="store_true", help="重新產生所有縮圖(換掉同名原圖時使用)")
    ap.add_argument("--no-pull", action="store_true", help="不先從 GitHub 取得最新內容")
    args = ap.parse_args()
    dry = args.dry_run
    log = print

    if not (dry or args.no_pull):
        pull_latest(log)

    data = json.loads(PHOTOS_JSON.read_text(encoding="utf-8"))
    by_slug = {c["slug"]: c for c in data}

    # images/ 底下有新的分類資料夾(例如 c30_小熊) -> 加進清單,名稱取底線後的部分
    for folder in sorted(p for p in IMAGES.iterdir() if p.is_dir()):
        if folder.name not in by_slug:
            name = CATEGORY_PREFIX.sub("", folder.name) or folder.name
            cat = {"slug": folder.name, "name": name, "icon": "📁", "files": []}
            data.append(cat)
            by_slug[folder.name] = cat
            log(f"新分類 {name}(圖示預設 📁,想換請到 photos.json 修改 icon)")

    added = removed = thumbs_made = 0
    for cat in data:
        folder = IMAGES / cat["slug"]
        if not folder.is_dir():
            if cat["files"]:
                log(f"[{cat['name']}] 找不到資料夾 {folder.relative_to(ROOT)},清單清空")
                removed += len(cat["files"])
                cat["files"] = []
            continue

        normalize_names(folder, dry, log)

        if dry:
            # dry-run 時檔案沒真的改名,用預期的結果來計算
            existing = {p.name for p in folder.glob("*.jpg") if STANDARD_NAME.match(p.name)}
            n = next_number(folder)
            extra = [p for p in folder.iterdir()
                     if p.is_file() and p.suffix.lower() in IMAGE_EXTS and not STANDARD_NAME.match(p.name)]
            existing |= {f"{n + i:03d}.jpg" for i in range(len(extra))}
            files = sorted(existing)
        else:
            files = sorted(p.name for p in folder.glob("*.jpg") if STANDARD_NAME.match(p.name))

        new = [f for f in files if f not in cat["files"]]
        gone = [f for f in cat["files"] if f not in files]
        if new:
            log(f"[{cat['name']}] 新增 {len(new)} 張:{', '.join(new)}")
        if gone:
            log(f"[{cat['name']}] 原圖已刪除,移出清單:{', '.join(gone)}")
        added += len(new)
        removed += len(gone)
        cat["files"] = files

        thumb_dir = THUMBS / cat["slug"]
        for fn in files:
            src, dst = folder / fn, thumb_dir / fn
            if args.rebuild_thumbs or not dst.exists():
                thumbs_made += 1
                if not dry:
                    make_thumb(src, dst)
        for fn in gone:
            t = thumb_dir / fn
            if t.exists():
                log(f"  刪除多餘縮圖 {t.relative_to(ROOT)}")
                if not dry:
                    t.unlink()

    if not dry:
        PHOTOS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        html = INDEX_HTML.read_text(encoding="utf-8")
        line = "var DATA=" + json.dumps(data, ensure_ascii=False) + ";"
        html, count = DATA_LINE.subn(lambda _: line, html, count=1)
        if count != 1:
            sys.exit("錯誤:index.html 裡找不到 `var DATA=...;` 這一行,未更新 index.html")
        INDEX_HTML.write_text(html, encoding="utf-8", newline="\n")

    total = sum(len(c["files"]) for c in data)
    prefix = "(dry-run,未修改檔案)" if dry else ""
    log(f"\n{prefix}完成:新增 {added} 張、移除 {removed} 張、產生縮圖 {thumbs_made} 張。"
        f"目前共 {len(data)} 個分類、{total} 張。")


if __name__ == "__main__":
    main()
