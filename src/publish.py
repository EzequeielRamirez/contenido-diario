"""Publica el video en Instagram Reels, Facebook Reels y TikTok (según qué credenciales existan)."""
import os, time, requests
GRAPH = "https://graph.facebook.com/v21.0"
def _raise(r):
    if not r.ok: raise RuntimeError(f"{r.request.method} {r.url.split('?')[0]} -> {r.status_code}: {r.text[:400]}")
    return r.json()

def instagram(video_url, caption):
    uid, tok = os.environ["IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    c = _raise(requests.post(f"{GRAPH}/{uid}/media", data={"media_type": "REELS", "video_url": video_url, "caption": caption, "share_to_feed": "true", "access_token": tok}, timeout=60))["id"]
    for _ in range(60):
        s = _raise(requests.get(f"{GRAPH}/{c}", params={"fields": "status_code,status", "access_token": tok}, timeout=30))
        if s["status_code"] == "FINISHED": break
        if s["status_code"] in ("ERROR", "EXPIRED"): raise RuntimeError(f"IG procesamiento falló: {s}")
        time.sleep(10)
    else: raise RuntimeError("IG: timeout procesando")
    return _raise(requests.post(f"{GRAPH}/{uid}/media_publish", data={"creation_id": c, "access_token": tok}, timeout=60))["id"]

def facebook(video_url, caption):
    pid, tok = os.environ["FB_PAGE_ID"], os.environ["META_PAGE_TOKEN"]
    st = _raise(requests.post(f"{GRAPH}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok}, timeout=60))
    vid, up = st["video_id"], st["upload_url"]
    _raise(requests.post(up, headers={"Authorization": f"OAuth {tok}", "file_url": video_url}, timeout=120))
    for _ in range(60):
        s = _raise(requests.get(f"{GRAPH}/{vid}", params={"fields": "status", "access_token": tok}, timeout=30))
        ph = s.get("status", {}).get("uploading_phase", {}).get("status")
        if ph == "complete": break
        if ph == "error": raise RuntimeError(f"FB subida falló: {s}")
        time.sleep(8)
    return _raise(requests.post(f"{GRAPH}/{pid}/video_reels", data={"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED", "description": caption, "access_token": tok}, timeout=60))

def tiktok(path, caption):
    """EXPERIMENTAL / sin probar. Con app sin auditar TikTok solo deja el video en privado (SELF_ONLY)."""
    tok = os.environ["TIKTOK_ACCESS_TOKEN"]; size = os.path.getsize(path)
    h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"}
    init = _raise(requests.post("https://open.tiktokapis.com/v2/post/publish/video/init/", headers=h, json={
        "post_info": {"title": caption[:150], "privacy_level": os.environ.get("TIKTOK_PRIVACY", "SELF_ONLY")},
        "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}}, timeout=60))
    up = init["data"]["upload_url"]
    with open(path, "rb") as f:
        r = requests.put(up, data=f, headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size-1}/{size}"}, timeout=300)
    if not r.ok: raise RuntimeError(f"TikTok subida: {r.status_code} {r.text[:300]}")
    return init["data"]["publish_id"]

def publish_all(path, caption):
    url = os.environ.get("VIDEO_URL"); results, errors = {}, {}
    jobs = []
    if os.environ.get("IG_USER_ID") and os.environ.get("META_PAGE_TOKEN") and url: jobs.append(("instagram", lambda: instagram(url, caption)))
    if os.environ.get("FB_PAGE_ID") and os.environ.get("META_PAGE_TOKEN") and url: jobs.append(("facebook", lambda: facebook(url, caption)))
    if os.environ.get("TIKTOK_ACCESS_TOKEN"): jobs.append(("tiktok", lambda: tiktok(path, caption)))
    if not jobs: raise SystemExit("No hay credenciales/URL: nada que publicar. Revisá los secrets.")
    for n, fn in jobs:
        try: results[n] = fn(); print("OK", n, results[n])
        except Exception as e: errors[n] = str(e); print("ERROR", n, e)
    if errors and not results: raise SystemExit(1)     # falla solo si no salió ninguna red
