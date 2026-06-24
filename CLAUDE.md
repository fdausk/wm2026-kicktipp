# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Was ist das?

Vollautomatisches Kicktipp-System für WM 2026. Claude analysiert WM-Spiele anhand externer Quellen (Wettquoten, xG, Aufstellungen, etc.) und gibt Tipps automatisch bei [kicktipp.com](https://www.kicktipp.com) in der Community **tip-it-like-i22** als Spieler **ClaudeFC** ab.

## Wichtige Befehle

```bash
# Dashboard im Browser öffnen (nötig für fetch() aus dashboard_data.json)
./serve.sh

# Spieltagsanalyse manuell starten (schreibt tipps_aktuell.json + dashboard_data.json)
./tipp-analyse [ST3]

# Tipps manuell eintragen (mit Bestätigungsschritt)
./tipps-eintragen [ST3]
```

Beide Skripte laden `.env` automatisch und rufen Claude über `claude -p` / `claude` auf.

### kicktipp-agent (MCP-Subprojekt)

```bash
cd kicktipp-agent
npm run build     # TypeScript kompilieren
npm test          # Tests ausführen
```

## Architektur & Datenfluss

```
Analyse (analyse.md)
  → liest:  dashboard_data.json, ergebnisse.json, performance.json
  → schreibt: dashboard_data.json (analysisTip, conf, note, injuries, analysisTs,
                                   meta.teamOdds, meta.teamOddsTs, meta.aktualisiert)
              tipps_aktuell.json (Begründungstexte)
              ergebnisse.json (aktuelle Turnierdaten)

Eintragen (eintragen.md)
  → liest:  dashboard_data.json (analysisTip, conf)
  → ruft:   mcp__kicktipp__place_bets auf
  → schreibt: dashboard_data.json (tip, tipsSubmitted, meta.rang, meta.aktualisiert)
              performance.json (Ergebnis-Tracking)

Dashboard (dashboard.html)
  → fetch('./dashboard_data.json') alle 60s
  → Offline-Fallback: GROUPS_PLACEHOLDER / KNOCKOUT_PLACEHOLDER (eingebettete JS-Konstanten)
  → Starten: ./serve.sh (python3 HTTP-Server auf Port 8080)
```

**Goldene Regel:** Match-Daten in `dashboard_data.json` pflegen — `dashboard.html` ist reiner Display-Layer. CSS/JS-Änderungen am Dashboard sind erlaubt; Spieldaten niemals direkt in `dashboard.html` eintragen.

## GitHub Pages

Das Dashboard ist öffentlich erreichbar unter: **https://fdausk.github.io/wm2026-kicktipp/**

- Passwortschutz: SHA-256 Client-Side via Web Crypto API + `sessionStorage` (Passwort nicht im Repo)
- Nur `dashboard.html`, `dashboard_data.json` und `index.html` werden versioniert (`.gitignore` Whitelist)
- Git-Author: immer `ClaudeFC <claude@kicktipp.local>` — niemals Klarnamen committen
- Nach jeder Analyse / Tippabgabe wird `dashboard_data.json` automatisch gepusht (AUSGABE-Schritt in `prompts/analyse.md` und `prompts/eintragen.md`)

```bash
git add dashboard_data.json
git commit -m "Analyse: Spieltag <nr> aktualisiert (<datum>)"
git push
```

## Zentrale Datei: `dashboard_data.json`

Single Source of Truth für alle Spieldaten. Struktur:

```json
{
  "meta": {
    "aktualisiert": "<ISO-UTC>",
    "rang": { "platz": "15.", "punkte": 4, "total": 24, "spieltag": "Spieltag 3" },
    "teamOdds": { "Spanien": 0.182, "Frankreich": 0.174, "Deutschland": 0.067, ... },
    "teamOddsTs": "<ISO-UTC>"
  },
  "spieltag_info": [ { "nr": 1, "analysisTs": "<ISO-UTC>", "tipsSubmitted": true } ],
  "st_starts_utc": [ null, "2026-06-11T19:00:00Z", ... ],
  "groups": {
    "A": { "teams": "...", "matches": [
      { "date": "DD.MM HH:MM", "home": "...", "away": "...",
        "tip": "2:1", "analysisTip": "2:1", "conf": "high", "quelle": "kalshi",
        "result": null, "injuries": "❌ ...", "note": "..." }
    ]}
  },
  "knockout": {
    "R32": [ { "id": "M73", "date": "...", "home": "...", "away": "...",
               "tip": null, "analysisTip": null, "conf": null,
               "result": null, "injuries": null, "note": null } ]
  }
}
```

- `date`-Felder sind **MESZ (UTC+2)**, Format `DD.MM HH:MM`
- `tip` = abgegebener Kicktipp-Tipp (nur durch `/tipps-eintragen` nach erfolgreichem `place_bets` setzen)
- `analysisTip` = Analyse-Empfehlung (durch `/tipp-analyse` setzen)
- `meta.aktualisiert` triggert Auto-Refresh im Dashboard
- `meta.teamOdds` = implizite Turniersieg-Wahrscheinlichkeiten pro Team (Kalshi/Betfair), deutsche Teamnamen als Keys
- `meta.teamOddsTs` = Timestamp des letzten Quoten-Fetches

## Automatisierung: `wm2026-match-watcher`

Läuft alle 15 Minuten via Claude Code Scheduled Tasks. Logik:

1. Turnier-Ende-Check (≥ 2026-07-20 → Task deaktivieren)
2. Spiele suchen: `result === null` AND (`tip === null` OR `tip !== analysisTip`) AND Anstoß 5–75 Min in der Zukunft
3. Aufstellungs-Gate (Fall A–D, Details in SKILL.md)
4. Vollanalyse per `prompts/analyse.md`
5. Automatischer Tipp per `mcp__kicktipp__place_bets` (kein Bestätigungsschritt)
6. `dashboard_data.json` pushen zu GitHub Pages

Task-Prompt: `/Users/felix.dauskardt/.claude/scheduled-tasks/wm2026-match-watcher/SKILL.md`

**Tipp-Aktualisierung:** Wenn `tip !== analysisTip`, wird der bestehende Kicktipp-Eintrag überschrieben. Der Watcher behandelt neue Tipps und Updates gleich.

## Prompt-Dateien

| Datei | Zweck |
|-------|-------|
| `prompts/analyse.md` | Vollständiger Analyse-Workflow (SCHRITT 0b–7 + AUSGABE) |
| `prompts/eintragen.md` | Tipp-Eintrage-Workflow inkl. Dashboard-Update und Performance-Tracking |

### Analyse-Schritte (Kurzübersicht)

- **0b** Performance.json lesen → Anpassungsregeln ableiten
- **0** Live-Turnierdaten: Kicktipp MCP (Rang, Schedule, Bets) + WebSearch (Ergebnisse, Gruppen, KO-Paarungen) + **Outright-Sieger-Quoten aller Teams → `meta.teamOdds`** (Kalshi/Betfair)
- **1** Verletzungen, bestätigte Aufstellungen, Saisonmüdigkeit
- **1b** Schiedsrichter-Profil
- **1c** Kartensperren & Gelbbelastung (🔴 Rotsperre, 🟨 Gelbsperre, ⚠️ auf Bewährung)
- **2** Wettquoten + Line Movement (Pinnacle, Betfair, Kalshi) + **Correct-Score-Markt (Top-3 Betfair)** + **Over/Under 2.5 Tore**
- **3** xG / Formkurve (FootyStats, FBref) + **Taktischer Archetyp-Match** (Low-Block-Erkennung)
- **4** Head-to-Head
- **5** Stadion, Klima, Diaspora-Faktor + **Ruhezeiten zwischen Spielen**
- **6** Turnier-Kontext + **ST3-Motivationsanalyse** (Gleichzeitigkeit, Durchkomm-Szenarien)
- **7** (KO only) Elfmeterschießen-Kompetenz

Konfidenz-Werte: `high` | `med-high` | `med`

### Anpassungsregeln (aus `prompts/analyse.md` SCHRITT 0b)

| Regel | Bedingung | Wirkung |
|-------|-----------|---------|
| ~~Knappe Favoriten~~ | ~~Favorit 52–65%~~ | ~~Unentschieden gleichwertig tippen~~ → **abgeschafft** (0/5 Trefferquote) |
| Score-Dämpfung | nach Favorit-% | ≤85%: max. 1 Tor Vorsprung, kein Unentschieden → 1:0 für Favoriten. 85–92%: max. 3 Tore Vorsprung. >92%: kein Deckel. |
| Außenseiter-Regel | Außenseiter ≥ 42% non-loss (Draw + Win) | Score um 1 Tor defensiver; wenn Ergebnis Unentschieden wäre → 1:0 Favorit |
| Eröffnungsspiel | Erstes Turnierspiel **+ mind. 1 Faktor**: keine Aufstellung / Schlüsselverletzung / Spielpause >6 Mo. | max. `med-high` |

Liegen keine Zusatzfaktoren vor, gilt beim Eröffnungsspiel kein Konfidenz-Deckel.

## Injuries-Feld Format

```
"injuries": "🔴 Vinicius Jr. (gesperrt noch 2 Sp.) | 🟨 Bellingham (GES) | ❌ Gnabry | ⚠️ Kroos (1 Gelb)"
```

| Emoji | Bedeutung |
|-------|-----------|
| 🔴 | Rotsperre |
| 🟨 | Gelbsperre |
| ❌ | Verletzungsausfall |
| ⚠️ | fraglich / auf Bewährung |
| ✅ | fit bestätigt (nur wenn zuvor zweifelhaft) |

## Dashboard: K.O.-Prognose

Die K.O.-Phase hat zwei Toggle-Ansichten:

- **🔮 Prognose** (Standard): Berechnet client-seitig aus `analysisTip`/`result` + `meta.teamOdds` den vorhergesagten Turniersieger
- **📋 Turnierbaum**: Klassischer Bracket mit abgegebenen Tipps

**Prognose-Engine (`buildPrediction()` in `dashboard.html`):**
1. Liegt ein `result` vor → echten Sieger daraus ablesen (reale KO-Ergebnisse haben Vorrang)
2. Sonst, liegt `analysisTip` vor → Sieger daraus ableiten
3. Sonst: Team mit höherer `meta.teamOdds`-Wahrscheinlichkeit gewinnt
4. Fallback (beide 0): `rankMap` (grobe FIFA-Tier-Einstufung)

Die globale JS-Variable `TEAM_ODDS` wird beim Laden aus `meta.teamOdds` befüllt. Die Prognose wird bei jedem `renderAll()`-Aufruf (= bei jedem Daten-Refresh alle 60s) neu berechnet.

## Dashboard: Mobile-Breakpoint (≤ 768px)

Die Gruppenphase-Tabellen verwenden auf Mobile ein 5-Spalten-Layout:

| Datum | Paarung | Score | S | K |
|-------|---------|-------|---|---|
| 11.06 / 21:00 | MEX vs RSA | `2:1` / `2:0` | ~ | 🟢 |

- **Datum**: Format `DD.MM / HH:MM` (MESZ)
- **Paarung**: 3-Letter FIFA-Abkürzungen aus `TEAMS_ABBR` in `dashboard.html`
- **Score**: Tipp / Ergebnis zusammengeführt (auf Desktop getrennte Spalten)
- **S**: Status-Icon (`—` ausstehend, `📌` getippt, `✓` richtig, `~` Tendenz, `✗` falsch)
- **K**: Konfidenz-Icon (`🟢` hoch, `🟡` mittel-hoch, `🟠` mittel) — Analyse-Text entfällt
- Desktop-Spalten `hide-mob`, Mobile-Spalten `show-mob` per CSS-Toggle

## kicktipp-agent (Subprojekt)

TypeScript CLI + MCP-Server für kicktipp.com. Nutzt Playwright/Chromium für Headless-Scraping (kein öffentliches API).

- Credentials: `~/.config/kicktipp-agent/config.ini` oder Env-Vars `KICKTIPP_EMAIL` / `KICKTIPP_PASSWORD`
- MCP-Tools die dieser Workflow nutzt: `place_bets`, `get_leaderboard`, `get_schedule`, `get_overview`, `get_status`
- Session-Caching: Nach erstem Login werden Sessions wiederverwendet

## Performance-Tracking

`performance.json` protokolliert jeden abgegebenen Tipp nach Spielende:
- Kategorien: `korrekt` / `tendenz` (Sieger richtig, Score falsch) / `falsch`
- `fehltipp_log`: Fehlschläge mit Typ (`unentschieden_uebergewichtet` etc.) für Bias-Erkennung
- `quellen_tracking`: Genauigkeit pro Quelle → beeinflusst Quellen-Gewichtung in SCHRITT 0b
