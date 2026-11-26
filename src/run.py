"""Uso: python src/run.py <slot> [--dry-run] [--no-wait]
Genera el video del día para el slot y lo publica a la hora Argentina indicada."""
import sys, os, time, datetime, json
sys.path.insert(0, os.path.dirname(__file__))
import common, make_video, publish, host
def main():
    slot = sys.argv[1]; dry = "--dry-run" in sys.argv; nowait = "--no-wait" in sys.argv
    hhmm, _ = common.SLOTS[slot]
    day = common.today(); idx, (title, lines, queries) = common.pick(slot, day)
    cta = common.CTAS[(day.toordinal() + idx) % len(common.CTAS)]
    out = f"out/{day.isoformat()}_{slot}.mp4"; os.makedirs("out", exist_ok=True)
    secs = make_video.build(lines, queries, cta, out, seed=day.toordinal() * 10 + idx, wd=f"work_{slot}")
    cap = common.caption(title, lines)
    json.dump({"slot": slot, "title": title, "caption": cap, "seconds": secs, "file": out}, open(f"out/{slot}.json", "w"), ensure_ascii=False)
    print(f"[{slot}] '{title}' listo: {secs:.1f}s -> {out}")
    if dry: return
    if os.environ.get('GITHUB_ACTIONS'): os.environ['VIDEO_URL'] = host.upload(out, slot)
    if not nowait:                       # esperar la hora exacta (Argentina)
        h, m = map(int, hhmm.split(":")); target = datetime.datetime.combine(day, datetime.time(h, m), tzinfo=common.ART)
        wait = (target - datetime.datetime.now(common.ART)).total_seconds()
        if wait > 0: print(f"esperando {wait/60:.1f} min hasta {hhmm} ART"); time.sleep(wait)
    publish.publish_all(out, cap)
if __name__ == "__main__": main()
