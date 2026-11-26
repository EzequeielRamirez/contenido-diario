import os, datetime, importlib, zoneinfo
ART = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")
# slot -> (hora ART, módulo del banco, tema)
SLOTS = {
  "almuerzo": ("12:30", "bank_almuerzo"),
  "regreso":  ("18:30", "bank_regreso"),
  "sillon":   ("21:30", "bank_sillon"),
}
CTAS = [
 "Todo el método está en la guía ¿Qué Le Mando Mañana? Tenés el enlace en la bio.",
 "Si querés las viandas de toda la semana resueltas, la guía está en el enlace de la bio.",
 "Armé todo esto paso a paso en la guía ¿Qué Le Mando Mañana? El enlace está en la bio.",
 "Para tener el plan completo, tocá el enlace de la bio y mirá la guía.",
]
HASHTAGS = "#viandas #viandasescolares #freidoradeaire #vueltaalcole #organizacion #mamasargentinas #recetasfaciles"
def today(): return datetime.datetime.now(ART).date()
def pick(slot, day=None):
    day = day or today()
    bank = importlib.import_module(SLOTS[slot][1]).BANK
    idx = (day.toordinal()) % len(bank)
    return idx, bank[idx]
def caption(title, lines):
    return f"{lines[0]}\n\n{lines[2]}\n\nEl método completo está en el enlace de la bio. 👆\n\n{HASHTAGS}"
