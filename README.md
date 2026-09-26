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

| Soutěž | Tipy | Výsledky | Vyhodnoceno |
|---|---|---|---|
| MS 2026 | 28 tipujících | obě časovky | průběžné pořadí |
| Giro 2026 | 29 tipujících | kompletní | ano |
| Vuelta 2026 | 52 tipujících | chybí | ne |
| Tour 2026 | zatím nepřepsáno | kompletní | ne |

Jarní klasiky 2026 (série devíti závodů) jsou zmapované, ale zatím
nepřevedené do strojového formátu.

## Anonymizace

Přezdívky tipujících jsou nahrazeny identifikátory `Tipujici_01` až
`Tipujici_61`. Přiřazení je **stabilní napříč všemi soutěžemi** —
`Tipujici_07` je v Giru i na Vueltě tatáž osoba, takže jde sledovat
výkon v čase. Převodní tabulka na skutečné přezdívky se nezveřejňuje.

Jména závodníků uvedena jsou; jde o veřejně známé sportovce a bez nich by
data nedávala smysl.

> **Pro přispěvatele:** tenhle repozitář je *výstup* anonymizace, ne
> pracovní kopie. Tipy se přepisují lokálně se skutečnými přezdívkami
> a teprve pak se vygeneruje veřejná verze. Převodní tabulka
> přezdívka → identifikátor zůstává mimo repozitář. Když do soutěže
> přibude tipující, celé číslování se přegeneruje, aby zůstalo
> abecední a konzistentní napříč soutěžemi.

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

Skutečné výsledky. Vyplňuje se ručně, stačí příjmení závodníka —
diakritika ani křestní jméno nevadí, párování si s tím poradí.

```
kategorie;poradi;jezdec
GC;1;Pogacar
GC;2;Gall
GC;3;
Vrchar;1;Carapaz
```

Nevyplněné řádky se ignorují, takže soubor slouží i pro **průběžné
pořadí** — po každé etapě nebo závodu stačí doplnit, co už se ví,
a spustit vyhodnocení znovu.

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

## Jak přidat novou soutěž

1. **Založ složku** `souteze/<nazev>/` (např. `tour-2027`).

2. **Zjisti, co se tipuje.** Projdi tipy v Discordu a sepiš kategorie.
   Nespoléhej na to, že jsou stejné jako minule — Giro nemá bojovníka
   ani horské prémie, Tour je má, MS má místo dresů čtyři závody.
   Nápověda k názvosloví je v [CTENI_TIPU.md](CTENI_TIPU.md).

3. **Zjisti bodování.** Tohle z dat vyčíst nejde — pořadatel ho vyhlašuje
   v podcastu, do Discordu ho nepíše. **Zeptej se.** Dokud ho nevíš,
   napiš do sloupce `zdroj` hodnotu `NUTNO OVERIT`, ať je vidět, že jde
   o odhad.

4. **Vytvoř `kategorie.csv`:**

   ```
   kategorie;typ;body_1;body_2;body_3;body_jinde;zdroj;popis
   GC;podium;50;30;20;10;zadal poradatel;Celkové pořadí
   Vrchar;jeden;30;;;;zadal poradatel;Puntíkovaný dres
   ```

5. **Přepiš tipy do `tipy.csv`.** U každého tipu vyplň `tip_raw`
   (doslova, jak to napsal) i `tip_kanonicky` („Příjmení Jméno").
   Nové přezdívky a překlepy přidej do `aliasy.csv`.

6. **Vytvoř prázdný `skutecne_vysledky.csv`** s řádky pro všechny
   kategorie a pozice.

7. **Spusť testy a vyhodnocení:**

   ```bash
   python test_vyhodnoceni.py
   python vyhodnoceni.py souteze/tour-2027
   ```

### Na co si dát pozor při přepisu

- **Tip s poznámkou „(upraveno)" se nepočítá.** Pořadatel vyhlásil
  striktní zákaz editace — takový tip do `tipy.csv` vůbec nepiš.
- **Chybějící kategorie není chyba.** Když někdo něco nevyplnil, prostě
  za ni nedostane body. Nedopisuj, co si myslíš, že chtěl.
- **Nejasný tip nehádej.** Když nevíš, do které kategorie tip patří nebo
  koho znamená přezdívka, **zeptej se a uveď od koho a kdy tip je**.
  Vymyšlené přiřazení vypadá v datech věrohodně a chyba se projeví až
  v bodech.
- **Tip po uzávěrce** platí, pokud ho pořadatel výslovně pustil do hry.

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
