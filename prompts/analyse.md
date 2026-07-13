Du führst die Spieltagsanalyse für Kicktipp WM 2026 durch.
Community: tip-it-like-i22 | Spieler: ClaudeFC

Arbeite die folgende Checkliste Schritt für Schritt vollständig ab. Kein Schritt ist optional.
Wenn eine Quelle nicht erreichbar ist, vermerke das explizit und stufe die Konfidenz für betroffene Spiele herab.

---

## WELCHER SPIELTAG WIRD ANALYSIERT?

Falls der Nutzer beim Aufruf explizit eine Spieltagnummer angegeben hat (z.B. `/tipp-analyse ST3`), diesen Spieltag verwenden.

Ansonsten: Analysiere den Spieltag mit dem **nächsten offenen Tipp-Fenster** — d.h. den Spieltag mit der frühesten noch nicht abgelaufenen Deadline, für den in `dashboard_data.json` (`spieltag_info`) noch `tipsSubmitted: false` gesetzt ist. Falls mehrere Spieltage gleichzeitig offen sind, den mit der frühesten Deadline wählen.

Gib zu Beginn der Analyse kurz aus, welcher Spieltag analysiert wird und warum (z.B. „Analysiere Spieltag 2 — früheste offene Deadline: 14.06 17:00 UTC").

Berechne anschließend, wie viele Stunden es bis zum ersten Anpfiff des Spieltags sind.
Falls mehr als 24 Stunden verbleiben, gib folgenden Hinweis aus — **bevor die Analyse beginnt**:

> ⚠️ **Hinweis: Analyse mehr als 24 Stunden vor Spielbeginn**
> Aufstellungen, Verletzungen und Wettquoten können sich noch erheblich ändern.
> Die Genauigkeit dieser Analyse ist daher eingeschränkt. Eine erneute Analyse
> kurz vor Spielbeginn (< 24h) wird empfohlen.

Die Analyse wird trotzdem vollständig durchgeführt — der Hinweis dient nur zur Information.

---

## SCHRITT 0b — Bisherige Tipp-Performance laden (VOR der Analyse)

Lies `performance.json` im Projektverzeichnis und wende die folgenden Anpassungen auf die gesamte nachfolgende Analyse an:

### Automatische Anpassungsregeln

**Wichtig: Die Regeln 1–3 werden in genau dieser Reihenfolge sequentiell auf den Rohscore angewendet.** Erst Score-Dämpfung, dann Außenseiter-Regel, dann Eröffnungsspiel-Deckel. Niemals parallel oder in anderer Reihenfolge.

1. **Score-Dämpfung:** Abhängig von der Gewinnwahrscheinlichkeit des Favoriten:
   - **≤ 65%:** Vorsprung maximal 1 Tor. Aus `2:0` wird `1:0`, aus `3:1` wird `2:1`. **Kein Unentschieden** — knappe Spiele enden in WM 2026 statistisch häufiger mit knappem Sieg als mit Remis (empirisch: 0/5 korrekt). Bei Unentschieden-Tendenz: 1:0 für den Favoriten bevorzugen.
   - **65–85%:** Vorsprung maximal 2 Tore. Aus `3:0` wird `2:0`. **Kein Unentschieden.** (Empirisch ab 2026-07-01: 9/9 `score_zu_konservativ`-Fehltipps mit bekanntem Favoriten-% lagen bei 75–88% — der bisherige 1-Tor-Deckel für dieses gesamte Band war systematisch zu defensiv, z.B. FRA 79% → 3:0 statt getippt 2:0, MEX 75% → 2:0 statt getippt 1:0.)
   - **85–92%:** Vorsprung maximal 3 Tore. Aus `4:0` wird `3:0`, höhere Scores bleiben bis 3-Tor-Margin. (Empirisch: Blow-out-Siege bei >85% Favoriten treten regelmäßig auf — NED 5:1, JPN 0:4, ESP 4:0; 2-Tor-Cap war zu defensiv.)
   - **> 92%:** Kein Deckel — Rohscore übernehmen. Extreme Favoriten gegen sehr schwache Gegner dominieren regelmäßig hoch (GER 7:1, USA 4:1, SWE 5:1).

   **Wichtig für die K.O.-Phase:** Diese Regel steuert ausschließlich die Tordifferenz (Vorsprung), niemals das Ergebnis-Format. Sie darf unter keinen Umständen zu einem echten Unentschieden (`H == G` ohne `n.E.`/`n.V.`-Suffix) führen — das gilt unverändert und wird zusätzlich durch den Abschluss-Pflichtcheck in SCHRITT 7 abgesichert (K.O.-Spiele haben laut FIFA-Reglement immer einen Sieger, ein Kicktipp-Tipp muss das Endergebnis nach Elfmeterschießen abbilden).

   **K.O.-Score-Wahl-Override (ab 2026-07-06 — überschreibt die obigen Bänder für K.O.-Spiele):**
   - **Favorit ≤ 85% (90 Min):** Standard-Score `"2:1"` (bzw. `"1:2"` bei Auswärtsfavorit) — Margin 1, aber nicht der minimale `"1:0"`-Tipp. Das 65–85%-Band mit max. 2 Toren aus Regel 1 gilt in der K.O.-Phase **nicht**.
   - **Favorit 85–92%:** Standard-Score `"3:0"` — das erlaubte 3-Tor-Band voll ausschöpfen, nicht defensiv auf `"2:0"`/`"2:1"` ausweichen.
   - **Favorit > 92%:** unverändert, kein Deckel.
   - **Ausnahme:** Bei Under-2.5-Marktsignal > 65% bleibt `"1:0"`/`"0:1"` der Standard (siehe SCHRITT 2).

   Begründung: Selbstaudit vom 2026-07-06 (20 K.O.-Spiele, 17/20 korrekte Sieger). 65% der Spiele endeten mit Margin 1, aber das häufigste konkrete Ergebnis war `2:1` (5×) — nicht `1:0` (3×). `2:1` schlägt `1:0` strategisch: korrekt bei `2:1`-Ergebnissen, Differenz sowohl bei `1:0` als auch bei `3:2` (inkl. n.V.-Aggregaten wie Belgien 3:2). Counterfactual: +4 Punkte auf 17 Spiele bei durchgängigem `2:1`-Tipp statt der bisherigen Praxis. Zusätzlich gewannen Frankreich (89%) und Spanien (87%) im 85–92%-Band beide exakt `3:0` — defensive `2:0`/`2:1`-Tipps kosteten dort weitere 4 Punkte, weil das erlaubte 3-Tor-Band nicht ausgeschöpft wurde.

2. **Außenseiter ≥ 42%:** Auf das Ergebnis aus Regel 1: Score um 1 Tor defensiver tippen (aus `2:1` wird `1:1`, aus `3:1` wird `2:1`). Die nicht-Verlust-Wahrscheinlichkeit (Draw + Win) des Außenseiters muss ≥ 42% betragen. **Wenn die reduzierte Version Unentschieden ergibt** (z.B. `1:0` → `0:0`): stattdessen `1:0` für den Favoriten wählen. **Wenn der Rohscore nach Regel 1 bereits einen Außenseiter-Sieg zeigt** (z.B. `0:1`): Regel 2 entfällt — kein weiterer Eingriff, Außenseiter-Sieg so tippen.

3. **Eröffnungsspiel eines Teams im Turnier:** Konfidenz maximal `mittel-hoch` **nur wenn** mindestens einer der folgenden Faktoren vorliegt:
   - Keine Aufstellungsbestätigung verfügbar
   - Schlüsselspieler verletzt oder fraglich
   - Team ohne Pflichtspieleinsatz in den letzten 6 Monaten
   
   Liegt keiner dieser Faktoren vor, gilt kein Deckel — ein 90%+-Favorit kann weiterhin `hoch` erhalten.

### Ausgabe

Gib am Beginn der Analyse einen kurzen Performance-Block aus:
```
📊 Tipp-Performance bisher: X korrekt | Y Differenz | Z Tendenz | W falsch (N Spiele) — Trefferquote: P% [(X×4+Y×3+Z×2)/(N×4)]
Aktive Anpassungsregeln: [Liste der greifenden Regeln für diesen Spieltag]
```

Falls `performance.json` nicht existiert oder leer ist, diesen Schritt überspringen und mit SCHRITT 0 fortfahren.

---

## SCHRITT 0 — Live-Turnierdaten abrufen (IMMER ZUERST)

### Kicktipp MCP (Spieler-Status)

Führe folgende Abfragen aus:

1. `mcp__kicktipp__get_leaderboard` → aktueller Rang ClaudeFC, Punkte, Teilnehmerzahl
2. `mcp__kicktipp__get_schedule` → anstehende Spiele, Deadlines
3. `mcp__kicktipp__get_overview` → offene Tipps, bereits abgegebene Tipps

**Kicktipp nicht für Turnierdaten verwenden** — Ergebnisse, Gruppenstand und K.O.-Paarungen sind dort unvollständig oder verzögert.

### Turnierdaten aus dem Web (primäre Quelle)

Suche via WebSearch + WebFetch nach:

4. Aktuelle WM 2026 Ergebnisse aller bisher gespielten Spiele → **Sofascore, CBS Sports oder FIFA.com**
5. Aktuelle Gruppenstandtabellen (Punkte, Tore, GD) → **Sofascore / Google „WM 2026 Gruppe X"**
6. K.O.-Paarungen, sofern bereits feststehend → aus aktuellem Gruppenstand ableiten oder direkt von FIFA.com / Sofascore abrufen

7. **WM 2026 Outright-Sieger-Quoten** → Kalshi (`kalshi.com/markets/kxmenworldcup/mens-world-cup-winner`) oder Betfair/Oddschecker als Fallback. Für alle noch im Turnier befindlichen Teams die implizite Gewinnwahrscheinlichkeit berechnen (= `100 / (AmericanOdds + 100)` für negative Quoten bzw. `100 / (DecimalOdds * 100)` für Dezimalquoten). Ergebnis als `meta.teamOdds` in `dashboard_data.json` speichern:
   ```json
   "teamOdds": { "Spanien": 0.18, "Frankreich": 0.16, "Deutschland": 0.065, ... }
   ```
   Bereits ausgeschiedene Teams auf `0` setzen. Nur Teams aus `dashboard_data.json` groups/knockout aufnehmen (deutsche Teamnamen verwenden). Quoten-Update bei jeder Analyse durchführen — vor allem nach K.O.-Runden aktualisieren.

Verwende ausschließlich diese Web-Quellen für `ergebnisse.json` (Ergebnisse, Gruppen, ko_paarungen).

Speichere das Ergebnis in `ergebnisse.json` im Projektverzeichnis mit folgendem Schema:
```json
{
  "aktualisiert": "<ISO-Timestamp>",
  "spieltag_aktuell": <nr>,
  "ergebnisse": [
    { "match_id": "M01", "heim": "...", "gast": "...", "ergebnis": "2:1", "datum": "YYYY-MM-DD" }
  ],
  "gruppen": {
    "A": [
      { "team": "...", "sp": 2, "s": 1, "u": 1, "n": 0, "tore": "3:1", "punkte": 4 }
    ]
  },
  "ko_paarungen": [
    { "runde": "R32", "match_id": "M73", "heim": "2A", "gast": "2B", "aufgeloest": false },
    { "runde": "R32", "match_id": "M73", "heim": "Spanien", "gast": "USA", "aufgeloest": true }
  ]
}
```
Einträge in `ko_paarungen`: `aufgeloest: false` solange Platzhalter, `aufgeloest: true` sobald Teams feststehen.

---

## SCHRITT 1 — Verletzungen, Kader & Aufstellung (für jedes anstehende Spiel)

Suche via WebSearch + WebFetch:

**Verletzungen & Ausfälle:**
- ESPN Injury Tracker: bestätigte Ausfälle
- Yahoo Sports / Goal.com / Squawka: Aufstellungstrends, Pressekonferenz-Statements

**Bestätigte Startelf (< 24h vor Anpfiff: höchste Priorität):**
- Offizielle Twitter/X-Accounts der Nationalverbände (z.B. @DFB_Team, @USMNT) — posten Startelf meist 60–75 min vor Anpfiff
- Sofascore Lineups-Tab: zeigt bestätigte oder voraussichtliche Formation
- ESPN / BBC Sport: „confirmed lineup" oder „predicted lineup" Artikel

**Aufstellungs-Status dokumentieren** (Pflichtfeld für jeden Tipp):

| Status | Bedeutung | Auswirkung auf `conf` |
|--------|-----------|----------------------|
| ✅ Beide bestätigt | Offizielle Startelf beider Teams bekannt | kein Abzug |
| ⚠️ Nur ein Team | Startelf nur eines Teams bekannt | max. `mittel-hoch` |
| ❌ Keines bestätigt, >15 Min | Noch zu früh | Analyse verschieben falls automatisiert; manuell: max. `mittel-hoch` + Hinweis in `note` |
| ❌ Keines bestätigt, <15 Min | Deadline zu nah | Analyse trotzdem — max. `mittel` + `⚠️ Aufstellung nicht bestätigt` in `note` |

Wenn eine bestätigte Startelf vorliegt, überschreibt sie alle anderen Kader-Signale. Halte fest:
- Formation (z.B. 4-3-3)
- Fehlen Schlüsselspieler trotz Fitness-Freigabe (taktische Schonung)?
- Überraschende Starter oder ungewohnte Positionen?

**Saisonabschluss-Müdigkeit:**
Für beide Teams prüfen: Bis wann liefen die Klubs-Spieler in der Saison? Spieler aus CL-Finalisten oder späten nationalen Pokalrunden tragen erhöhte Ermüdung — besonders relevant in ST1–ST2.
- Quelle: Transfermarkt Spielerprofil (Einsatzminuten laufende Saison) oder kurze WebSearch „[Spieler] minutes played 2025/26"
- Faustregel: >3500 Minuten Klubsaison + WM-Spieltag 1 oder 2 = Konfidenz-Abzug bei physisch intensiven Prognosen

---

## SCHRITT 1b — Schiedsrichter (für jedes anstehende Spiel)

FIFA veröffentlicht Schiedsrichter-Ansetzungen ca. 2–3 Tage vor dem Spiel.

Suche: `"[Heim] vs [Gast] WM 2026 referee"` oder direkt FIFA.com Matchcenter.

Für jeden Schiedsrichter ermitteln:
- Durchschnittliche Karten pro Spiel (gelb + rot)
- Elfmeter-Häufigkeit pro Spiel
- Bekannte Tendenz: eng pfeifend / laissez-faire?
- Quelle: Transfermarkt Schiedsrichterprofil (`/schiedsrichter/X/profil/schiedsrichter/X`) oder WhoScored Referee Stats

**Wirkung auf den Tipp:**
- Referee mit hoher Elfmeter-Rate bei ausgeglichenem Spiel → Elfmeter-Szenario wahrscheinlicher:
  - Favorit **>92%**: Score um +1 Tor erhöhen (kein Score-Deckel aktiv)
  - Favorit **85–92%**: Elfmeter-Bonus maximal bis an 3-Tor-Cap heranführen
  - Favorit **≤85%**: Score-Dämpfung würde +1 Tor sofort wieder kappen — stattdessen in `note` vermerken und `conf` halten
- Sehr restriktiver Referee → Tore-Erwartung leicht senken (aus `2:1` wird eher `1:0`)
- In K.O. besonders relevant: Elfmeterschießen-Wahrscheinlichkeit steigt bei stark spielkontrollierendem Referee

---

## SCHRITT 1c — Kartensperren & Gelbbelastung (für jedes anstehende Spiel)

Suche via WebSearch + WebFetch nach aktueller Kartenbilanz aller Stammspieler beider Teams.

**Quellen:**
- FIFA.com Match Center / Turnierstatistiken: offizielle Gelb-/Rot-Karten-Zählung pro Spieler
- Sofascore Turnierstatistiken: Karten kumuliert pro Spieler
- Transfermarkt: Sperren-Übersicht

**WM 2026 Suspensions-Regeln:**

| Situation | Sperre |
|-----------|--------|
| 2 Gelbe Karten (Gruppenphase) | 1 Gruppenspiel gesperrt |
| Gelbe Karten aus Gruppenphase | Reset nach Achtelfinale |
| Rote Karte | Mindestens 1 Spiel (FIFA-Disziplinarkommission entscheidet über Verlängerung) |
| 2 Gelbe in einem Spiel | Gleichwertig Platzverweis → 1 Spiel gesperrt |

**Auswirkung auf den Tipp:**

| Situation | Wirkung |
|-----------|---------|
| Schlüsselspieler gesperrt | Gleichwertig mit Verletzungsausfall → `conf` sinkt; in `injuries` eintragen |
| Schlüsselspieler auf 1 Gelb, wichtiges Folge-Spiel | Coach könnte schonen → `note` mit Hinweis, kein `conf`-Abzug |
| Mehrere Stammspieler auf 1 Gelb | Score-Erwartung defensiver tippen |

**Darstellung im `injuries`-Feld:**

```
"injuries": "🔴 Vinicius Jr. (gesperrt noch 2 Spiele) | 🟨 Bellingham (GES) | ⚠️ Kroos (1 Gelb)"
```

| Emoji | Bedeutung |
|-------|-----------|
| `🔴` | Rotsperre (1+ Spiele) |
| `🟨` | Gelbsperre (2. Gelbe → 1 Spiel gesperrt) |
| `⚠️` | Auf Bewährung (1 Gelbe, wichtiges Folge-Spiel) |
| `❌` | Verletzung / Ausfall |

Bei relevanter Rotsperre zusätzlich im `note`-Feld vermerken, ab wann der Spieler zurückkehrt (z.B. `"🔴 Vinicius Jr. gesperrt — Rückkehr frühestens QF"`).

---

## SCHRITT 2 — Wettmarkt & Line Movement (frisch, nicht älter als 24h vor Anstoß)

Für jedes Spiel:

**Aktuelle Quoten:**
- Betfair Exchange: schärfster Indikator (implizierte Wahrscheinlichkeiten)
- Bet365 / DraftKings: 3-Weg Moneyline → implizierte Wahrscheinlichkeiten
- Kalshi / Polymarket: Prediction-Market-Konsens
- Dimers / SportsCasting Supercomputer: wahrscheinlichster Endstand
- Forebet: Statistische Score-Prognose mit xG

**Line Movement (Quoten-Veränderung der letzten 48h):**
- Pinnacle (schärfste Wettbörse, minimale Marge): aktuelle Quote + Opening Line vergleichen
- Oddschecker Line Movement Tab: zeigt historischen Quotenverlauf
- Suche: `"[Heim] vs [Gast] odds movement"` oder `"line movement [Heim] [Gast] World Cup"`

**Interpretation:**
- Quote zieht um >5 Prozentpunkte zugunsten eines Teams → signifikantes Signal (oft Aufstellungs-/Fitness-News eingepreist)
- Quote bewegt sich gegen Erwartung (Außenseiter wird kürzer) → Kontra-Signal, Konfidenz senken
- Kein Movement trotz Analyse-Zeitraum von 48h → Markt sieht kein klares Bild → Score defensiv halten (`1:0` statt `2:1`) und `conf` um eine Stufe senken

**Correct-Score-Markt (Betfair / Pinnacle):**
Abrufen der Top-3 meistgehandelten Ergebnisse im Correct-Score-Markt.
- Wenn das marktführende Ergebnis um mehr als 1 Tor vom eigenen geplanten Tipp abweicht → Score anpassen oder `conf` eine Stufe senken
- Wenn 1:1 oder 0:0 unter den Top-2 Ergebnissen → Signal für enges Spiel; Score enger tippen (z.B. `2:1` → `1:0`). **Kein Unentschieden** — stattdessen `1:0` für den Favoriten (Score-Dämpfung-Regel gilt auch hier)

**Over/Under 2.5 Tore:**
Implizierte Under-2.5-Wahrscheinlichkeit aus Betfair/Pinnacle ableiten.
- Under 2.5 > 65% → Kein Score mit ≥3 Toren gesamt — erlaubte Scores: `1:0` oder `0:1` (kein `1:1` in der Gruppenphase — Score-Dämpfung verbietet Unentschieden). **K.O.-Ausnahme:** `"1:1 n.E. (Team)"` ist bei Under 2.5 erlaubt (= 2 Tore reguläre Spielzeit), da es kein Remis ist.
- Over 2.5 > 65% → Score mit ≥3 Toren gesamt bevorzugen (`2:1`, `3:0`, etc.)

---

## SCHRITT 3 — Formkurve & xG-Statistik

- FootyStats / FBref: xG letzte 3–5 Spiele beider Teams
- ESPN Stats / Opta: Ø Tore, Ø kassiert, W/D/L letzte 5–10 Spiele
- Ab ST 3: Turnierspiele überschreiben Qualifikationsdaten

**Taktischer Archetyp-Match:**
Für jeden Außenseiter prüfen (WebSearch: `"[Team] defensive system WM 2026"` oder `"[Team] low block formation"`):
- Spielt das Team tief (Low-Block, 5er-Kette, Konter-System)? → 1 Tor vom erwarteten Favoriten-Score abziehen und `conf` um eine Stufe senken
- Indikator: Marokko, Katar, Türkei, Australien, Costa Rica, Albanien, Slowenien gelten als bekannte Low-Block-Teams
- Gilt auch für KO-Phase, jedoch mit geringerem Effekt (nur Score-Abzug, kein conf-Abzug), da Außenseiter sich öfter öffnen müssen

**Remis-Risiko-Warnung:**
WM 2026 produziert strukturell überdurchschnittlich viele Remis (~37 % beobachtet vs. ~27 % historischer WM-Schnitt). Wenn **beide** folgenden Bedingungen zutreffen, füge im `note`-Feld den Vermerk `"⚠️ Remis-Risiko"` hinzu und senke `conf` um eine Stufe (Deckel bei `med`):
1. Außenseiter-xG der letzten 3 Spiele ≥ 0.8 pro Spiel (tatsächliche Gefährlichkeit trotz Außenseiter-Status)
2. Favorit ≤ 85 % Gewinnwahrscheinlichkeit (angehoben von 75% am 2026-07-02 — Katar-Schweiz (84%) und England-Ghana (80%) endeten beide 0:0/1:1 und lagen außerhalb der alten Schwelle)

**Keinen Remis-Tipp setzen** — das Turnier produziert Remis, aber die empirische Trefferquote von Remis-Tipps liegt bei 0 %. Stattdessen bleibt der Score-Tipp (z.B. 1:0), aber mit reduzierter Konfidenz. Der note-Vermerk hilft, das Muster in performance.json nachzuvollziehen.

**K.O.-Phase:** Auch mit angehobener Schwelle gilt unverändert: Diese Regel darf niemals selbst einen Unentschieden-Tipp erzeugen. Sie senkt nur `conf` und dokumentiert das Risiko im `note`-Feld. In der K.O.-Phase greift zusätzlich SCHRITT 7 (Elfmeterschießen-Kompetenz) — ein erhöhtes Remis-Risiko bei einem Favoriten ≤85% ist dort ein zusätzliches Signal dafür, das `"1:1 n.E. (Team)"`-Format statt eines knappen reinen Sieges zu erwägen, niemals aber ein reines `H:H`-Unentschieden zu tippen.

---

## SCHRITT 4 — Head-to-Head

- FootyStats H2H: alle Direktduelle
- FIFA.com / Soccerway: WM- und EM-Duelle höher gewichten als Freundschaftsspiele

---

## SCHRITT 5 — Stadion, Klima & Umfeld

Für jedes Spiel prüfen:

**Physische Bedingungen:**
- Dach/Klimaanlage: Houston NRG, Dallas AT&T, Atlanta MBS, Vancouver BC Place = kein Hitzefaktor
- Temperaturen bei Freistadien (Miami, Kansas City, etc.)
- Höhenlage: Mexico City Azteca = 2240m → südamerikanische Teams bevorzugt
- Quelle: Stammdaten + Weather.com / Climate Central

**Heimunterstützung bei neutralem Spielort:**
US-Städte mit großer Diaspora verwandeln neutrale Spiele faktisch in Heimspiele — dies ist in Wettquoten oft nicht vollständig eingepreist.
- Los Angeles, Miami, Houston, Chicago: stark lateinamerikanisch (Mexiko, Argentinien, Brasilien, Kolumbien profitieren)
- New York/New Jersey: diverse Diaspora, kein klarer Vorteil
- Vancouver, Seattle: europäische/asiatische Fans gut vertreten
- Suche: `"[Stadt] WM 2026 [Team] fans atmosphere"` für konkrete Berichte

Wirkung: bei Spielen mit erkennbarem Fanvorteil → Außenseiter leicht aufwerten (max. 1 Tor näher an Favoriten, z.B. aus `2:0` wird `1:0` oder aus `2:1` bleibt `2:1` statt `3:1`)

**Ruhezeiten zwischen Spielen:**
Für beide Teams: Datum des letzten Pflichtspiels ermitteln (aus `ergebnisse.json` oder WebSearch).
- Differenz ≥ 2 Tage Ruhe zugunsten eines Teams → dieses Team um 0.5 Tore aufwerten (z.B. aus `1:1` wird `2:1`)
- Besonders relevant in KO-Phase und bei intensiven Turnierphasen (3 Spiele in 9 Tagen)

---

## SCHRITT 6 — Turnier-Kontext (aus Schritt 0 verwenden)

- Bisherige WM-Ergebnisse beider Teams: Siege, Niederlagen, Tordifferenz
- Aktuelle Gruppenposition und Druck (qualifiziert? ausgeschieden? muss gewinnen?)
- Gewichtung Turnier-Formkurve: ST1=0%, ST2=6%, ST3+=12%, K.O.=15%

**ST3-Motivation (nur Spieltag 3 der Gruppenphase):**
Beide Gruppen-Paarungen laufen gleichzeitig — Teams kennen das Parallel-Ergebnis nicht. Prüfen:
- Wenn Team A mit Unentschieden weiterkommt UND Team B ebenfalls mit Unentschieden weiterkommt → enges Spiel, Score defensiver tippen (z.B. `2:1` → `1:0`). **Kein Unentschieden** — Score-Dämpfung-Regel gilt auch hier (empirisch: Teams spielen bei veränderter Spielsituation doch auf Sieg)
- Wenn ein Team bereits ausgeschieden ist und rotiert → klarer Spielstärke-Vorteil für das noch qualifizierbare Team, aber Score-Erwartung senken (kein Hochsieg)
- Quelle: aktueller Gruppenstand aus `ergebnisse.json` + Parallelspiel-Paarung aus `dashboard_data.json`

---

## SCHRITT 7 — Nur K.O.-Phase: Elfmeterschießen-Kompetenz

(Nur ausführen wenn aktuelle Spiele zur K.O.-Phase gehören)

Kicktipp-Regel K.O.: Tipp muss Ergebnis NACH Elfmeterschießen berücksichtigen — inkl. Sieger.

- Torwart-Save-Rate (5%): FBref PKatt/PK + FIFA.com WM-PE-Rekorde
- Team-PE-Bilanz (3%): Transfermarkt /elfmeterschiessen/
- Schützen-Verfügbarkeit (2%): FBref + ESPN Injury Tracker
- Schiedsrichter-Elfmeter-Rate (aus SCHRITT 1b): hohe Rate erhöht PE-Wahrscheinlichkeit im regulären Spiel, damit auch das Risiko dass das Spiel bereits 90min entschieden wird

**Wichtig (Korrektur 2026-07-13):** `"1:1 n.E. (Team)"` behauptet wörtlich, dass das Spiel nach Elfmeterschießen entschieden wird — die maximal mögliche Spieldauer. Empirisch traf das nur 1 von 4 bisher gespielten `n.E.`-Tipps zu (M78, M92, M94 wurden alle in der regulären Spielzeit entschieden, nur M88 ging tatsächlich in die Verlängerung/Elfmeter). Da der K.O.-Pflicht-Check beim Eintragen ohnehin **immer** einen normalen entscheidenden Score ableitet (`submitTip` = `"2:1"`/`"1:2"`, niemals der `n.E.`-String selbst), bringt das Format keinen Punktevorteil — es behauptet nur einen meist falschen Spielverlauf. Die Elfmeter-Kompetenz dient daher nur noch als **Tiebreaker für die Sieger-Wahl**, nicht mehr als Format-Entscheidung.

Konfidenz-Entscheidung (nach Favorit-Gewinnwahrscheinlichkeit in 90 Min) — Score in allen Fällen gemäß K.O.-Score-Wahl-Override in SCHRITT 0b (`"2:1"`/`"1:2"` bei ≤85%, `"3:0"` bei 85–92%):
- **>65%:** Sieger = Favorit aus Wettquoten. Normaler Fall, keine Elfmeter-Erwägung nötig.
- **45–65%:** Sieger = Favorit aus Wettquoten, **außer** die Elfmeter-Kompetenz des Außenseiters ist eindeutig überlegen (Torwart-Bilanz 50% + Team-PE-Bilanz 30% + Schützen-Verfügbarkeit 20%) — dann Sieger = Außenseiter.
- **<45% (kein klarer Favorit):** Sieger = Team mit der besseren Gesamtbewertung aus den gleichen drei Elfmeter-Kriterien. Score direkt als normalen Sieg tippen (z.B. `"2:1"` wenn Sieger Heimteam, `"1:2"` wenn Auswärtsteam) — **kein** `n.E.`-Suffix.

`"1:1 n.V. (Team)"`/`"1:1 n.E. (Team)"` bleibt als Format verfügbar, aber nur wenn ein **konkretes, matchspezifisches Signal** für eine sehr lange Spieldauer vorliegt (z.B. beide Teams historisch extrem defensiv/kartenscheu, Schiedsrichter-Profil mit auffällig wenig Elfmetern und Karten, explizite Marktdaten mit hoher Over-120-Minuten-Quote) — nicht als Standardformat für „knapp"/„kein klarer Favorit".

**Abschluss-Pflichtcheck (K.O.-Phase):** Bevor `analysisTip` in `dashboard_data.json` geschrieben wird: Prüfe, ob der Tipp ein reines Unentschieden ist — d.h. beide Torwerte identisch und kein `n.V.`- oder `n.E.`-Suffix (Beispiele: `"1:1"`, `"0:0"`, `"2:2"`). Ist dies der Fall: Tipp ist **ungültig**, da K.O.-Spiele immer einen Sieger haben. Den Favoriten ermitteln und stattdessen `"1:0"` (bzw. `"0:1"`) tippen. Unentschieden-Tipps dürfen niemals in `dashboard_data.json` für K.O.-Matches stehen.

---

## AUSGABE — tipps_aktuell.json schreiben

Ermittle den exakten Timestamp via `date -u +"%Y-%m-%dT%H:%M:%SZ"` (falls nicht bereits in Schritt AUSGABE 1 geschehen) und verwende ihn für `erstellt`.

Speichere die Tipp-Empfehlungen in `tipps_aktuell.json` im Projektverzeichnis:

```json
{
  "erstellt": "<ISO-Timestamp aus date-Befehl>",
  "spieltag": <nr>,
  "phase": "gruppe|ko",
  "rang": { "platz": 15, "punkte": 2, "teilnehmer": 24 },
  "tipps": [
    {
      "match_id": "M01",
      "heim": "Deutschland",
      "gast": "USA",
      "anstoss": "2026-06-15T21:00:00Z",
      "deadline": "2026-06-15T21:00:00Z",
      "empfehlung": "2:1",
      "konfidenz": "hoch",
      "begruendung": "Deutschland klarer Favorit (Betfair 72%), starke xG-Werte..."
    }
  ]
}
```

Konfidenz-Werte: `hoch` | `mittel-hoch` | `mittel` (in `tipps_aktuell.json`). Für `dashboard_data.json` → `"conf": "high"` | `"med-high"` | `"med"` (englische Bezeichnungen laut Schema).

**Konfidenz-Abzüge** (automatisch anwenden, wenn ein Kriterium zutrifft):
- Keine bestätigte Startelf verfügbar → max. `mittel-hoch`
- Line Movement gegen erwartete Richtung (>5 Pkt.) → max. `mittel`
- Schiedsrichter unbekannt oder Daten fehlen → keine Änderung, aber in `begruendung` vermerken
- Saisonabschluss-Müdigkeit bei ≥3 Stammspielern eines Teams → Konfidenz eine Stufe senken
- Diaspora-Faktor stark zugunsten des nominellen Außenseiters → Score defensiver tippen

**Empirisch (M5 — ab 2026-06-25):** `high` nur bei Favorit >90% ODER (bestätigte Startelf beider Teams UND Außenseiter xG < 0.5 in letzten 3 Spielen). Bei ≤90% Favorit ohne beide Bedingungen: max. `med-high`. (Basis: 10 Spiele, high 45% vs. med-high 50% — Übervertrauen bei Dominanzprognosen gegen kompakte Außenseiter.)

**M5-Verschärfung K.O.-Phase (ab 2026-07-06):** `high` ist für die gesamte restliche K.O.-Phase deaktiviert — Maximum ist `med-high`, unabhängig von der Favoriten-Wahrscheinlichkeit. (Basis: ST11-Review, n=15 `high`-Tipps, Quote 46.7% vs. 53.1% bei `med-high` — die Inversion aus der ursprünglichen M5-Analyse besteht seit ST7 trotz der 90%-Schwelle fort. K.O.-Einzelspiele sind volatiler als Formkurven-basierte Gruppenspiele, Dominanzprognosen bleiben unzuverlässig.)

---

## AUSGABE — dashboard_data.json aktualisieren

**Wichtig:** Alle Match- und Analysedaten werden ausschließlich in `dashboard_data.json` geschrieben — `dashboard.html` wird nicht mehr direkt bearbeitet. Das Dashboard lädt die JSON-Datei automatisch beim Öffnen und alle 60 Sekunden neu.

Vorgehen: Read `dashboard_data.json` → Felder anpassen → Write `dashboard_data.json` (komplette Datei überschreiben).

### 1. analysisTs für den aktuellen Spieltag setzen

Ermittle zuerst den exakten Ausführungszeitpunkt via Bash:
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```
Verwende **ausschließlich** diesen Wert. In `spieltag_info` den Eintrag mit `nr == <spieltag>` finden und `analysisTs` setzen:
```json
{ "nr": 3, ..., "analysisTs": null }
→ { "nr": 3, ..., "analysisTs": "2026-06-16T18:00:00Z" }
```

Gleichzeitig `meta.aktualisiert` auf denselben Timestamp setzen — das triggert den Auto-Refresh im Dashboard.

### 2. Analyseempfehlungen schreiben

**WICHTIG: Das Feld `tip` wird hier NICHT gesetzt.** `tip` darf ausschließlich durch `/tipps-eintragen` nach erfolgreichem `place_bets` geschrieben werden. Nur `analysisTip`, `conf` und `note` aktualisieren.

Felder:
- `analysisTip`: empfohlener Tipp — Gruppenphase z.B. `"2:1"`, K.O.-Phase z.B. `"1:1 n.E. (Spanien)"`
- `conf`: `"high"` | `"med-high"` | `"med"`
- `note`: kurze Begründung (1–2 Sätze, max. 120 Zeichen)

**Gruppenphase** — in `groups.X.matches` per `home` + `away` suchen:
```json
{ "home": "Katar", "away": "Schweiz", "analysisTip": null, "conf": null, "note": null }
→ { "home": "Katar", "away": "Schweiz", "analysisTip": "0:2", "conf": "high", "note": "Schweiz klarer Favorit (Kalshi 81%), Katar ohne WM-Sieg seit 2022." }
```

**K.O.-Phase** — in `knockout.X` per `id` suchen:
```json
{ "id": "M73", "analysisTip": null, "conf": null, "note": null }
→ { "id": "M73", "analysisTip": "2:1", "conf": "med-high", "note": "Spanien Favorit (Betfair 68%), USA Heimvorteil begrenzt durch starken Gegner." }
```

### 3. Spielergebnisse eintragen

Alle in `ergebnisse.json` enthaltenen Einträge mit gesetztem `ergebnis`-Feld (nicht null/leer) in `dashboard_data.json` übertragen.

Gruppenspiele: `groups.X.matches[i].result` per `home` + `away` setzen.
K.O.-Spiele: `knockout.X[i].result` per `id` setzen.

Nur gesicherte Endstände eintragen — laufende oder ungespielte Spiele auf `null` belassen.

### 4. Verletzungen / Kadernotizen aktualisieren

`injuries`-Feld in `groups.X.matches[i]` (Gruppenphase) bzw. `knockout.X[i]` (K.O.-Phase) aktualisieren.

- Format: `"🔴 Vinicius Jr. (gesperrt noch 2 Sp.) | 🟨 Bellingham (GES) | ❌ Gnabry | ⚠️ Kroos (1 Gelb)"`
- Status-Emojis: `🔴` = Rotsperre, `🟨` = Gelbsperre, `❌` = Verletzungsausfall, `⚠️` = fraglich / auf Bewährung (1 Gelbe), `✅` = fit bestätigt (nur wenn zuvor zweifelhaft)
- Nur Schlüsselspieler — kein Fließtext. Falls keine Ausfälle und keine Karten-Risiken: `null`.

### 5. Rang aktualisieren

`meta.rang` in `dashboard_data.json` auf aktuellen Stand setzen:
```json
"rang": { "platz": "15.", "punkte": 4, "total": 24, "spieltag": "Spieltag 3" }
```

### 6. K.O.-Paarungen (falls aufgelöst)

Falls in `ergebnisse.json` Einträge mit `aufgeloest: true` vorhanden sind: Placeholder-Teams (z.B. `"2A"`, `"W M73"`) in `knockout.X[i].home` / `.away` durch echte Teamnamen ersetzen.

---

Gib am Ende eine kurze Zusammenfassung aus:
- Welcher Spieltag analysiert wurde
- Wie viele Spiele analysiert wurden
- Rang aktuell
- Eventuelle Einschränkungen (nicht erreichbare Quellen)

### 7. Dashboard auf GitHub Pages veröffentlichen

```bash
cd /Users/felix.dauskardt/Documents/Claude/Projects/Kicktipp
python3 sync-placeholder.py
git add dashboard_data.json dashboard.html
git commit -m "Analyse: Spieltag <nr> aktualisiert (<datum>)"
git push
```

Ausgabe: „✅ Dashboard veröffentlicht: https://fdausk.github.io/wm2026-kicktipp/"
