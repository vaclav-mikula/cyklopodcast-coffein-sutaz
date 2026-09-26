# Tipovací soutěž CykloPodcast

Vyhodnocení tipovacích soutěží z Discord komunity [CykloPodcast](https://discord.com/channels/1088369417559212073/1140967779181264958),
pořádaných ve spolupráci s Coffein. Tipuje se podium vybraných závodů —
mistrovství světa, Grand Tour, jarní klasiky.

Repozitář obsahuje strojově čitelný přepis tipů, vyhodnocovací skript
a výsledná pořadí. Formát i skript jsou obecné, nezávislé na konkrétní akci.

## Co je v repozitáři

```
souteze/
    ms-2026/        mistrovství světa — 4 závody, podium
    vuelta-2026/    Vuelta — GC, dresy, tým, 30+, Peñas Blancas
    giro-2026/      Giro — GC, dresy, tým, 30+
    tour-2026/      Tour — jako Vuelta + bojovník a horské prémie
aliasy.csv          párování variant jmen závodníků
vyhodnoceni.py      výpočet pořadí
CTENI_TIPU.md       jak číst tipy z Discordu
```

**Stav dat:**

| Soutěž | Tipy | Výsledky |
|---|---|---|
| MS 2026 | 28 tipujících | obě časovky, hromadné závody se teprve pojedou |
| Vuelta 2026 | 52 tipujících | zatím nevyplněny |
| Giro 2026 | 29 tipujících | zatím nevyplněny |
| Tour 2026 | zatím nepřepsáno | — |

Jarní klasiky 2026 (série devíti závodů) jsou zmapované, ale zatím
nepřevedené do strojového formátu.

## Anonymizace

Přezdívky tipujících jsou nahrazeny identifikátory `Tipujici_01` až
`Tipujici_61`. Přiřazení je **stabilní napříč všemi soutěžemi** —
`Tipujici_07` je v Giru i na Vueltě tatáž osoba, takže jde sledovat
výkon v čase. Převodní tabulka na skutečné přezdívky se nezveřejňuje.

Jména závodníků uvedena jsou; jde o veřejně známé sportovce a bez nich by
data nedávala smysl.

## Bodování

| Situace | Body |
|---|---|
| Uhodnuté 1. místo | 50 |
| Uhodnuté 2. místo | 30 |
| Uhodnuté 3. místo | 20 |
| Závodník skončil na podiu dané kategorie, ale tipující ho měl jinde | 10 |
| Trefená jednotlivá kategorie (dres, tým, prémie) | 30 |
| Netrefeno | 0 |

Při shodě bodů se uděluje sdílené pořadí a následující pozice se přeskočí
(1, 1, 1, 4). Sekundárně se řadí abecedně, aby bylo pořadí stabilní mezi běhy.

## Dva typy kategorií

Soubor `kategorie.csv` v každé soutěži říká, co se tipuje a za kolik:

```
kategorie;typ;body_1;body_2;body_3;body_jinde;zdroj;popis
GC;podium;50;30;20;10;...;Celkové pořadí
Vrchar;jeden;30;;;;...;Puntíkovaný dres
```

- **`podium`** — tipují se tři místa, boduje se i závodník, který na podiu
  skončil, ale na jiné pozici (`body_jinde`)
- **`jeden`** — tipuje se jediný vítěz (dres, tým, horská prémie),
  body jen za přesnou trefu

Sloupec `zdroj` říká, odkud hodnota pochází. `NUTNO OVERIT` znamená, že
bodování bylo převzato z jiné soutěže a nebylo potvrzeno pořadatelem —
pravidla se vyhlašují v podcastu, ne v Discordu.

## Soubory jedné soutěže

### `tipy.csv`

Přepis tipů. Oddělovač `;`, kódování UTF-8 s BOM.

| Sloupec | Popis |
|---|---|
| `datum` | datum odeslání tipu (`YYYY-MM-DD`) |
| `cas` | čas odeslání (`HH:MM`) |
| `tipujici` | anonymizovaný identifikátor |
| `kategorie` | označení kategorie, viz `kategorie.csv` |
| `poradi` | tipované místo: `1`, `2` nebo `3` |
| `tip_raw` | jméno přesně tak, jak ho tipující napsal |
| `tip_kanonicky` | normalizovaný tvar „Příjmení Jméno" pro párování |

Sloupec `tip_raw` je zachován záměrně — tipy jsou psané velmi volně
(přezdívky, iniciály, překlepy, emoji, čtyři jazyky) a je užitečné vidět
originál vedle normalizovaného tvaru.

```
datum;cas;tipujici;kategorie;poradi;tip_raw;tip_kanonicky
2026-08-22;08:53;Tipujici_25;GC;1;Pogacar;Pogacar Tadej
2026-08-22;08:53;Tipujici_25;Sprinter;1;WVA;van Aert Wout
2026-08-19;16:20;Tipujici_51;Mladik;1;Torres;Torres Pablo
```

### `skutecne_vysledky.csv`

Skutečné výsledky. Vyplňuje se ručně, stačí příjmení závodníka.
Nevyplněné kategorie se ignorují, takže soubor slouží i pro průběžné
pořadí v průběhu akce.

### `vyhodnoceni_souteze.csv`

Výstup: `poradi;prezdivka;body`. Obsahuje všechny tipující včetně těch
s nulou.

### `pravidla.csv`

Název soutěže, období tipování a nastavení (dělené pořadí, zápis nulových).

## Spuštění

Bez závislostí, jen standardní knihovna Pythonu 3.

```bash
python vyhodnoceni.py souteze/vuelta-2026
```

Bez argumentu pracuje v kořenové složce. Vypíše pořadí na konzoli a zapíše
`vyhodnoceni_souteze.csv` do složky soutěže.

### Testy

```bash
python test_vyhodnoceni.py
```

Ověřují na vymyšlených datech, že bodování počítá správně: oba typy
kategorií, párování jmen včetně falešných shod, dělené pořadí a průběžné
vyhodnocení nedokončené soutěže. **Spouštět po každé změně `aliasy.csv`
nebo `vyhodnoceni.py`** — nejčastější chyba je příliš krátký alias, který
začne chytat cizí jména.

## Párování jmen

Nejpracnější část celé úlohy. Tipy přicházejí v naprosto volné formě a je
potřeba poznat, že jde o téhož závodníka:

- **jen křestní jméno** — `Remco` → Evenepoel, `Wout` → van Aert, `Jonas` → Vingegaard
- **přezdívky** — `Pogi`, `Torito`, `Pippo`, `MVDP`, `WVA`, `Jasper Disaster`,
  a dokonce `Ikeaman` → Arensman
- **diakritika** — `Backstedt` / `Bäckstedt`, `Kung` / `Küng`, `Roglic` / `Roglič`
- **překlepy** — `Noojien`, `Newiadoma`, `Del Torro`, `Carrapaz`, `Pogacat`
- **složená příjmení** — `Del Toro`, `Le Court-Pienaar`, `Paret-Peintre`,
  `O'Connor`, `Longo Borghini`, `Ferrand-Prévot`

Řeší se ve dvou krocích. Při přepisu z Discordu se každý tip ručně převede
na kanonický tvar „Příjmení Jméno" — křestní jména a přezdívky rozliší jen
člověk se znalostí startovní listiny. Skript pak porovnává příjmení, malými
písmeny a **bez diakritiky**. Víceslovná příjmení a přezdívky řeší
`aliasy.csv` (přes 100 položek).

> **Pozor při rozšiřování aliasů:** vzor se hledá i uvnitř jména, takže
> krátký vzor může chytit něco jiného. Po každé změně ověřte, že
> `Torres` nedává `del toro` a `Martin` se neplete s `Martinez`.

> **Pozor na diakritiku:** odstranění přehlásek se do skriptu dostalo
> dodatečně. Než tam bylo, `Backstedt` zapsaný do výsledků nesedl na
> `Bäckstedt` v tipech a body za to místo nedostal nikdo — přičemž výstup
> vypadal naprosto věrohodně. Když čísla nesedí, kontrolujte přehlásky
> jako první.

## Sběr dat

Tipy se z Discordu čtou přes prohlížeč, ručně, jako běžný člen kanálu.
Žádné uživatelské tokeny ani automatizace nad účtem — to
[Discord ToS](https://discord.com/terms) zakazuje.

Podrobnosti v [CTENI_TIPU.md](CTENI_TIPU.md): co které emoji znamená
(a že totéž emoji znamená u různých lidí něco jiného), jak se jmenují
tytéž kategorie v různých soutěžích, a proč se emoji musí číst z DOM
a ne z textu stránky.
