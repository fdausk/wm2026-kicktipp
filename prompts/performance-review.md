Du führst eine automatische Effizienzprüfung der Kicktipp-Analyse durch.
Ausgelöst von: Watcher nach Spieltag-Abschluss (alle Ergebnisse eingetragen).

---

## SCHRITT 1 — Datenbasis laden

Lies `performance.json` und `dashboard_data.json`.

Aus `performance.json` extrahieren:
- `gesamt` (gespielt, korrekt, differenz, tendenz, falsch)
- `fehltipp_log` (alle Einträge mit `typ`, `favorit_pct`, `conf`, Datum)
- `regelaenderungen` (um zu filtern: nur Fehler NACH dem letzten Regeländerungsdatum auswerten)

Aus `dashboard_data.json` extrahieren:
- Alle Spiele mit gesetztem `result` UND `tip` — prüfe ob `conf` und `quelle` gesetzt sind
- Für die Konfidenz-Analyse: Spiele nach `conf` (`high` / `med-high` / `med`) gruppieren

---

## SCHRITT 2 — Statistiken berechnen

Berechne folgende Kennzahlen. **Basis: nur Fehler nach dem letzten Regeländerungsdatum** (Feld `regelaenderungen[last].datum`). Falls keine Regeländerung vorhanden: alle Fehler auswerten.

### 2a — Gesamttrefferquote
```
Trefferquote = (korrekt×4 + differenz×3 + tendenz×2 + falsch×1) / (gespielt×4)
Zielwert: ≥ 60% (= ca. 2/3 der maximalen Punkte)
```

### 2b — Fehlerverteilung (nur nach letzter Regeländerung)
Zähle pro Fehlertyp:
- `favorit_gewann_nicht` — Favorit hat nicht gewonnen (Draw oder Upset)
- `aussenseiter_unterschaetzt` — Außenseiter gewann unerwartet klar
- `unentschieden_uebergewichtet` — Remis getippt, ein Team hat gewonnen
- `score_zu_konservativ` — Tendenz richtig, Score zu niedrig
- `sonstiges` — Score zu hoch oder nicht klassifizierbar

Anteil je Typ = N / Gesamtfehler × 100 %

### 2c — Konfidenz-Genauigkeit
Aus `dashboard_data.json` alle Spiele mit `result` und `conf`:
- Gruppiere nach `conf`: wie viele Spiele je Gruppe? Wie viele `korrekt` / `tendenz` / `falsch`?
- Erwartung: `high` > `med-high` > `med` (in Trefferquote)
- Falls `high` schlechter als `med`: konkretes Signal für Übervertrauen

### 2d — Favorit-% Analyse (nur `favorit_gewann_nicht` + `aussenseiter_unterschaetzt`)
Aus `fehltipp_log`-Einträgen mit gesetztem `favorit_pct`:
- Wo häufen sich die Fehler? Bereiche: <65% / 65–75% / 75–85% / >85%
- Anmerkung: im Bereich 75–85% ist die Score-Dämpfung aktiv, aber das Remis-Risiko ggf. nicht ausreichend gewürdigt

### 2e — Quellen-Tracking (falls Daten vorhanden)
Falls `quellen_tracking.kalshi`, `.betfair`, `.oddschecker` Einträge haben:
- Berechne Trefferquote pro Quelle
- Quelle mit >50% Fehlerquote bei ≥5 Spielen → `schlechte_quelle`-Flag setzen

---

## SCHRITT 3 — Musterprüfung (Schwellenwerte für Regeländerungen)

Prüfe folgende Bedingungen. Eine Regeländerung wird nur vorgenommen, wenn:
- Ausreichend Datenpunkte vorhanden (Schwellenwert pro Regel unten angegeben)
- Das Muster eindeutig ist (nicht durch Zufallsstreuung erklärbar)
- Die vorgeschlagene Änderung nicht kontraproduktiv zu einer bestehenden Regel ist

### Regel M1 — Remis-Risiko zu wenig genutzt
**Bedingung:** `favorit_gewann_nicht` ≥ 6 Fälle nach letzter Regeländerung  
**UND** Mehrheit dieser Fälle hatte `favorit_pct` zwischen 65–82%  
**→ Aktion:** In `prompts/analyse.md` den Schwellenwert für Remis-Risiko-Warnung senken:  
Statt `Favorit ≤ 75%` → `Favorit ≤ 80%` (eine Stufe breiter)  
Begründung in `regelaenderungen` dokumentieren.

### Regel M2 — Außenseiter zu oft unterschätzt
**Bedingung:** `aussenseiter_unterschaetzt` ≥ 5 Fälle nach letzter Regeländerung  
**UND** Ø `favorit_pct` dieser Spiele ≤ 67%  
**→ Aktion:** In `prompts/analyse.md` die Außenseiter-Regel verschärfen:  
Schwellenwert von 42% non-loss → 39% non-loss  
Begründung in `regelaenderungen` dokumentieren.

### Regel M3 — Score-Dämpfung zu aggressiv (>85% Grenze zu niedrig)
**Bedingung:** `score_zu_konservativ` ≥ 5 Fälle nach letzter Regeländerung  
**UND** Mehrheit dieser Fälle hatte `favorit_pct` > 85% (Grenzbereich 85–90%)  
**→ Aktion:** In `prompts/analyse.md` den Score-Dämpfung-Schwellenwert anpassen:  
Von 85% → 88% (Deckel greift erst bei niedrigerem Favoriten-Level)  
Begründung in `regelaenderungen` dokumentieren.

### Regel M4 — Score-Dämpfung zu locker (>85% Grenze zu hoch)
**Bedingung:** `favorit_gewann_nicht` ≥ 4 Fälle bei `favorit_pct` > 85% nach letzter Regeländerung  
**→ Aktion:** In `prompts/analyse.md` den Score-Dämpfung-Schwellenwert absenken:  
Von 85% → 82%  
Begründung in `regelaenderungen` dokumentieren.

### Regel M5 — Konfidenz-Übervertrauen
**Bedingung:** `high`-Conf-Spiele haben Trefferquote < `med-high`-Conf-Spiele bei ≥ 8 `high`-Spielen  
**→ Aktion:** In `prompts/analyse.md` unter SCHRITT AUSGABE einen Hinweis ergänzen:  
„Empirisch: `high` nur bei Favorit >90% ODER bestätigter Startelf + low xG Außenseiter"

---

## SCHRITT 4 — analyse.md aktualisieren (wenn Schwellenwerte erreicht)

Wenn eine oder mehrere der Muster-Bedingungen erfüllt sind:

1. Lies `prompts/analyse.md`
2. Suche die relevante Stelle (z.B. „Score-Dämpfung bei Favoriten ≤ 85%")
3. Ändere den Schwellenwert / Ergänze den Hinweis präzise — keine anderen Teile der Datei anfassen
4. Füge in `performance.json → regelaenderungen` einen neuen Eintrag hinzu:

```json
{
  "datum": "<YYYY-MM-DD>",
  "regel": "<Regelname>",
  "aktion": "aktualisiert",
  "grund": "<Muster-ID + Anzahl Fälle + Zeitraum>",
  "alt": "<alter Wert>",
  "neu": "<neuer Wert>"
}
```

---

## SCHRITT 5 — Spieltag-Review speichern

Füge in `performance.json` unter einem neuen Feld `spieltag_reviews` (Array) einen Eintrag hinzu:

```json
{
  "spieltag": <nr>,
  "datum": "<ISO-UTC>",
  "gespielt_gesamt": 48,
  "trefferquote_gesamt": 0.438,
  "trefferquote_aktuell": 0.51,
  "fehlerverteilung": {
    "favorit_gewann_nicht": 9,
    "aussenseiter_unterschaetzt": 5,
    "unentschieden_uebergewichtet": 6,
    "score_zu_konservativ": 3,
    "sonstiges": 8
  },
  "conf_accuracy": {
    "high": { "gespielt": 12, "korrekt": 2, "tendenz": 6, "falsch": 4, "quote": 0.46 },
    "med-high": { "gespielt": 18, "korrekt": 1, "tendenz": 8, "falsch": 9, "quote": 0.40 },
    "med": { "gespielt": 18, "korrekt": 1, "tendenz": 4, "falsch": 13, "quote": 0.33 }
  },
  "regelaenderungen_getriggert": ["M1"],
  "notiz": "<1-2 Sätze: wichtigste Erkenntnis dieses Reviews>"
}
```

Felder `trefferquote_aktuell` = nur Spiele nach letzter Regeländerung (zeigt ob neue Regeln wirken).

---

## AUSGABE

Gib am Ende aus:
```
📊 Performance-Review abgeschlossen (Spieltag <nr>)
   Trefferquote gesamt: X% | aktuell (post-Regeländerung): Y%
   Dominanter Fehlertyp: <typ> (<n> Fälle, <anteil>%)
   Regeländerungen: <M1, M2, ... oder "keine — Schwellenwerte nicht erreicht">
   Conf-Überraschung: <z.B. "high schlechter als med-high — 3/12 vs 4/18">
```

Falls keine Regeländerung ausgelöst wird: Ausgabe trotzdem vollständig — der Review-Eintrag in `performance.json` ist immer wertvoll für die Trendverfolgung.
