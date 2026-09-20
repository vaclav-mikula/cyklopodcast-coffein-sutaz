# Tipovací soutěž CykloPodcast

Vyhodnocení tipovacích soutěží z Discord komunity [CykloPodcast](https://discord.com/channels/1088369417559212073/1140967779181264958),
pořádaných ve spolupráci s Coffein. Tipuje se podium vybraných závodů —
mistrovství světa, Grand Tour, jarní klasiky.

Repozitář obsahuje strojově čitelný přepis tipů, vyhodnocovací skript
a výsledné pořadí. Formát i skript jsou obecné, nezávislé na konkrétní akci.

## Bodování

| Situace | Body |
|---|---|
| Uhodnuté 1. místo | 50 |
| Uhodnuté 2. místo | 30 |
| Uhodnuté 3. místo | 20 |
| Závodník skončil na podiu dané kategorie, ale tipující ho měl jinde | 10 |
| Závodník na podiu neskončil | 0 |

Při shodě bodů se uděluje sdílené pořadí a následující pozice se přeskočí
(1, 1, 1, 4). Sekundárně se řadí abecedně, aby bylo pořadí stabilní mezi běhy.

Jiné bodování stačí přepsat v konstantách `BODY_ZA_MISTO`
a `BODY_PODIUM_JINDE` na začátku skriptu.

## Anonymizace

Přezdívky tipujících jsou nahrazeny identifikátory `Tipujici_01`,
`Tipujici_02` a tak dál. Přiřazení je stabilní napříč soubory — `Tipujici_07`
je v tabulce tipů i ve výsledkovém pořadí tatáž osoba. Převodní tabulka
na skutečné přezdívky se nezveřejňuje.

Číslování ale platí vždy jen **v rámci jedné soutěže**. Při jiné sestavě
tipujících vyjde jinak, takže anonymizovaná data z různých soutěží nelze
spojovat.

Jména závodníků uvedena jsou; jde o veřejně známé sportovce a bez nich by
data nedávala smysl.

## Soubory

### `tipy.csv`

Přepis tipů z Discordu. Oddělovač `;`, kódování UTF-8 s BOM.

| Sloupec | Popis |
|---|---|
| `datum` | datum odeslání tipu (`YYYY-MM-DD`) |
| `cas` | čas odeslání (`HH:MM`) |
| `tipujici` | anonymizovaný identifikátor |
| `kategorie` | označení závodu, viz níže |
| `poradi` | tipované místo: `1`, `2` nebo `3` |
| `tip_raw` | jméno přesně tak, jak ho tipující napsal |
| `tip_kanonicky` | normalizovaný tvar „Příjmení Jméno" pro párování |

Sloupec `tip_raw` je zachován záměrně — tipy byly psány velmi volně
(přezdívky, iniciály, překlepy, různé jazyky) a je užitečné vidět originál
vedle normalizovaného tvaru.

```
datum;cas;tipujici;kategorie;poradi;tip_raw;tip_kanonicky
2026-09-19;11:48;Tipujici_15;ITT M;3;Soderqvist;Söderqvist Jakob
2026-09-19;14:43;Tipujici_16;RR M;1;Torito;Del Toro Isaac
2026-09-20;14:12;Tipujici_23;RR M;2;MVDP;van der Poel Mathieu
```

### `skutecne_vysledky.csv`

Skutečné výsledky závodů. Vyplňuje se ručně, stačí příjmení závodníka.
Nevyplněné kategorie se při vyhodnocení ignorují, takže soubor slouží
i pro průběžné pořadí v průběhu akce.

```
kategorie;poradi;jezdec
ITT W;1;Reusser
ITT W;2;Backstedt
ITT W;3;Koch
```

### `vyhodnoceni_souteze.csv`

Výstup skriptu: `poradi;prezdivka;body`, seřazeno od nejvyššího počtu bodů.
Obsahuje všechny tipující včetně těch s nulou.

### `aliasy.csv`

Víceslovná příjmení a varianty zápisu, které se mají považovat za téhož
závodníka. Nepovinný soubor; když chybí, fungují jen jednoslovná příjmení.

### `vyhodnoceni.py`

Vyhodnocovací skript. Bez závislostí, jen standardní knihovna Pythonu 3.

```bash
python vyhodnoceni.py
```

Očekává ostatní soubory ve stejné složce. Vypíše pořadí na konzoli
a zapíše `vyhodnoceni_souteze.csv`.

## Kategorie

Kategorie nejsou ve skriptu pevně dané — přečte si je z dat. Stačí používat
stejná označení v `tipy.csv` i `skutecne_vysledky.csv`.

Pro šampionát se čtyřmi závody se hodí třeba:

| Kód | Závod |
|---|---|
| `ITT M` | časovka jednotlivců, muži |
| `ITT W` | časovka jednotlivců, ženy |
| `RR M` | hromadný závod, muži |
| `RR W` | hromadný závod, ženy |

Pro jinou akci si lze zvolit vlastní — třeba `Etapa 1` až `Etapa 21`
nebo `Milán-San Remo`.

## Párování jmen

Nejpracnější část celé úlohy. Tipy přicházejí v naprosto volné formě a je
potřeba poznat, že jde o téhož závodníka:

- **jen křestní jméno** — `Remco` → Evenepoel, `Wout` → van Aert, `Lotte` → Kopecky
- **iniciály a přezdívky** — `MVDP`, `WVA`, `WvA`, `Torito`
- **diakritika** — `Backstedt` / `Bäckstedt`, `Kung` / `Küng`, `Soderqvist` / `Söderqvist`
- **překlepy** — `Noojien` / `Nooijen`, `Newiadoma` / `Niewiadoma`, `Del Torro` / `Del Toro`, `Hanna` / `Ganna`
- **složená příjmení** — `Le Court` / `Le Court-Pienaar`, `Longo Borghini`, `van der Poel`

Řeší se ve dvou krocích. Při přepisu z Discordu se každý tip ručně převede
na kanonický tvar „Příjmení Jméno" (sloupec `tip_kanonicky`) — křestní jména
a přezdívky rozliší jen člověk se znalostí startovní listiny. Skript pak
porovnává příjmení, malými písmeny a **bez diakritiky**, takže `Backstedt`
a `Bäckstedt` dávají stejný klíč. Víceslovná příjmení řeší `aliasy.csv`.

> **Pozor při rozšiřování:** odstranění diakritiky se do skriptu dostalo
> dodatečně. Než tam bylo, `Backstedt` zapsaný do výsledků nesedl na
> `Bäckstedt` v tipech a body za to místo nedostal nikdo — přičemž výstup
> vypadal naprosto věrohodně. Když čísla nesedí, kontrolujte přehlásky jako
> první.

## Sběr dat

Tipy se z Discordu čtou přes prohlížeč, ručně, jako běžný člen kanálu.
Žádné uživatelské tokeny ani automatizace nad účtem — to
[Discord ToS](https://discord.com/terms) zakazuje.

Jedna past stojí za zmínku: Discord vykresluje emoji jako `<img>`, takže
prosté vytažení textu stránky je zahodí. Někteří tipující ale označují
kategorie **jen** emoji (🚺/🚹 pro pohlaví, 🌈 pro duhový dres mistra světa).
Bez emoji se takový tip přiřadí ke špatnému závodu. Při čtení DOM je proto
potřeba brát v potaz atribut `alt` u obrázků.
