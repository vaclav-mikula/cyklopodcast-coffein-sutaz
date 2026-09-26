# Jak číst tipy z Discordu

Praktické poznámky ze čtení kanálu `#💥-sutaz-s-coffeein💥` — co které
emoji znamená, jak se tytéž kategorie jmenují u různých lidí a kde jsou
pasti. Sesbíráno z jarních klasik, Gira, Tour, Vuelty a MS 2026.

Tohle je doplněk k [README](README.md), kde je popsaný formát dat
a postup, jak přidat novou soutěž. Sem se dívej, když máš před sebou
konkrétní zprávu z Discordu a potřebuješ ji rozluštit.

**Tipy jsou vždy jen v kanálu `#💥-sutaz-s-coffeein💥`.** Kanály
`giro-d-italia`, `tour-de-france`, `vuelta-a-espana` a `tipovacka`
obsahují jen diskusi o závodech.

## Postup čtení

1. `preview_start` na URL kanálu, počkat ~6 s (Discord se načítá jako aplikace)
2. Rolovat nahoru: `computer` → `scroll` se souřadnicí **v prázdné části
   oblasti zpráv**, typicky `[600, 300]`. Když kurzor padne na zprávu,
   scroll se nechytí.
3. Mezi scrolly **čekat 2–3 s**, jinak Discord nestihne dopnout historii.
4. Číst přes DOM, ne přes `get_page_text` — viz níže.

Discord zprávy **virtualizuje**: starší se při rolování odpojují z DOM.
Sbírej průběžně po dávkách, ne až na konci.

## Při stahování hlídej značku „(upraveno)"

Editovaný tip **neplatí** (viz pravidla níže). Značku je proto nutné
zachytit hned při stahování a u tipu si ji poznamenat — když se zahodí
jako šum, později se nedá dohledat jinak než opakovaným čtením kanálu.

Discord ji vykresluje jako samostatný element vedle času:

```js
const editovano = !!li.querySelector('[class*="edited"]');
```

Tipy s touto značkou se do `tipy.csv` nezapisují a jejich autoři se
**vypíšou uživateli**, ať ví, koho se vyřazení týká.

## Emoji se musí číst z DOM

`get_page_text` emoji zahazuje, protože Discord je vykresluje jako `<img>`.
U některých tipujících jsou emoji **jediné** označení kategorie — bez nich
se tip přiřadí ke špatnému závodu.

```js
Array.from(document.querySelectorAll('li[id^="chat-messages"]')).map(li => {
  const a = li.querySelector('[class*="username"]')?.textContent || '';
  const ts = li.querySelector('time')?.getAttribute('datetime') || '';
  const b = li.querySelector('[id^="message-content"]');
  if (!b) return null;
  let t = '';
  const walk = n => {
    if (n.nodeType === 3) { t += n.textContent; return; }
    if (n.tagName === 'IMG' && n.alt) { t += '[' + n.alt + ']'; return; }
    if (n.tagName === 'BR') { t += '\n'; return; }
    n.childNodes.forEach(walk);
  };
  walk(b);
  return ts + '\t' + a + '\t' + t;
}).filter(Boolean).join('\n@@@\n')
```

Dá to i přesné timestampy z `<time datetime>`.

## Co které emoji znamená

Většina tipujících:

| Emoji | Kategorie |
|---|---|
| 🥇 🥈 🥉 nebo 👑 | pořadí v GC |
| 🌈 | mistr světa (1. místo na MS) |
| 🟢 💚 | zelený dres — sprinter, body |
| 🔵⚪ ⚪🔵 🔴⚪ ❤️🤍 | vrchař (puntíkovaný) |
| ⚪ 🤍 👼 | bílý dres — mladík |
| 🔴 💛 | vedoucí v GC (červený na Vueltě, žlutý na Tour) |
| 👨‍🦽 👴 🧔 🩶 ⛰️ | 30+ / staříci — **šedý dres** |
| 🏔️ 🗻 | Peñas Blancas / horská prémie |
| 🥊 💪 | bojovník |
| 🚄 | sprinter (Tipujici_02) |

**Šedý dres = 30+.** Potvrzeno z Gira 2026, kde Tipujici_15 píše přímo
„30+: šedý dres". To vysvětluje 🩶 u Tipujici_22a na Tour i ⛰️ u jeho skupiny
na Vueltě — všechno je táž kategorie, jen jiná ikona.

### Giro má vlastní barvy dresů

| Emoji | Kategorie na Giru |
|---|---|
| 🩷 | vedoucí v GC (maglia rosa je růžová) |
| 💜 🟣 | sprinter (maglia ciclamino je fialová, ne zelená) |
| 🔵 💙 | vrchař (maglia azzurra je modrá, ne puntíkovaná) |
| ⚪ 🤍 | mladík (maglia bianca) |

Na Giru tedy **🔵 není vrchař podle puntíků, ale podle modré** — nepleť
si to s Tour, kde 🔵⚪ znamená puntíkovaný.

Tipujici_35 jako jediný píše dresy italskými názvy: *Rosa / Ciclamino /
Azzurra / Bianca*. Tipujici_29 píše *Maglia ciclamino / azzurra / bianca*.

**Giro nemá bojovníka ani horské prémie** — na rozdíl od Tour.

### ⛰️ znamená u každého něco jiného

| Autor | Význam ⛰️ |
|---|---|
| Tipujici_11 (Giro) | **vrchař** — 30+ má zvlášť, označené medailemi |
| Tipujici_22, Tipujici_17, Tipujici_05, Tipujici_16 (Vuelta, Tour) | **30+** — následují tři jména |

Rozlišovací pravidlo: po ⛰️ následuje **jedno** jméno a 30+ je v tipu
jinde → vrchař. Následují **tři** jména → 30+.
| 🚹 🚺 | pohlaví (Tipujici_07 na MS) |
| 👨⏲️ 👧⏲️ 👨‍🦲🌈 🙍‍♀️🌈 | ITT M / ITT W / RR M / RR W (Tipujici_20 na MS) |

**Pozor na barevné dvojice** — 🔵⚪ a ⚪🔵 je totéž, jen v jiném pořadí.

### Skupina s vlastní sadou (Tipujici_22, Tipujici_17, Tipujici_05, Tipujici_16)

Čtyři lidé používají jinou sadu, zřejmě od sebe opisují:

| Emoji | Význam |
|---|---|
| ❤️🏆 nebo 💛 | 1. místo GC |
| 💚 | zelený dres |
| 🤍🩵 nebo 🤍❤️ | vrchař |
| 🤍 | bílý dres |
| 🩶 ⛰️ | **30+ (šedý dres)** — pak následují tři jména |
| 🧔 | 1. místo v 30+ |

Dříve jsem ⛰️ považoval za nejasné. Giro to vysvětlilo: šedý dres je 30+,
takže ⛰️/🩶 uvozuje trojici staříků, ne horskou prémii.

## Názvy kategorií — každý si je píše po svém

| Kategorie | Varianty v tipech |
|---|---|
| Vrchař | Vrchar, Vrchár, Vrchař, Vrchní, Puntíky, Bodky, Bodkovaný, Kopce, Hory, KOM |
| Sprinter | Sprinter, Zelený, Zeleny, Body, Bodovačka, Bodovací dres, Šprint, Sprint |
| Mladík | Mladík, Mlaďas, Mladý, Bílý, Biely, Bily, Baby |
| Tým | Tým, Tim, Tím, Team |
| 30+ | 30+, Nad 30, Starci, Staříci, Starci (na chmelu), Důchodci, Cena dona Alejandra, Don Alejandro |
| Bojovník | Bojovník, Bojovnik, Nejbojovnější, Super combatif, Combativ, Combativity, Combatitive, Červené číslo, Aktivita, Miss sympatia |
| Peñas Blancas | Penas Blancas, Peňas Blancas, Peñaz Blancas, Peñis Blancas, Penas Blanca, PB, Kávový kopec, Coffeein žolík |
| Tourmalet | Tourmalet, Souvenir Jacques Goddet, Jacques Goddet |
| Galibier | Galibier, Souvenir Henri Desgrange, Henri Desgrang |
| MS – časovka | ITT, ITT M/W, ITT ME/WE, TT, Časovka muži/ženy |
| MS – hromadný | RR, RR M/W, Race ME/WE, Elite M/Ž, ME/WE, Hromadný, Masák, Silniční závod |

## Jména závodníků

Aliasy jsou v `aliasy.csv`. Zásady:

- **Jednoslovná příjmení** fungují sama, do aliasů nepatří
- **Diakritika** se odstraňuje automaticky — `Kung`/`Küng`,
  `Backstedt`/`Bäckstedt`, `Roglic`/`Roglič` není potřeba zapisovat
- **Přezdívky** ano: `Pogi`, `Remco`, `Wout`, `Torito`, `Lotte`
- **Víceslovná příjmení** ano: `Del Toro`, `Le Court`, `Paret-Peintre`,
  `O'Connor`, `Longo Borghini`, `van der Poel`, `van Aert`

Pozor při přidávání aliasu: vzor se hledá i **uvnitř** jména, takže krátký
vzor může chytit něco jiného. Po každé změně `aliasy.csv` nebo
`vyhodnoceni.py` spustit testy:

```bash
python test_vyhodnoceni.py
```

Ověřují bodování obou typů kategorií, párování jmen (přezdívky, diakritika,
falešné shody), dělené pořadí a průběžné vyhodnocení. Ověřeno, že testy
skutečně selžou — zkušebně přidaný alias `tor` shodil párování jmen,
protože začal chytat i `Torres`.

### Zvláštní případy

- **Všetkými milovaný Sean Avery** píše přezdívky: `Lipo` = Lipowitz,
  `Ikeaman` = **Arensman**, `🌞🐐 (Pogi)` = Pogačar
- **Tipujici_07** připisuje poznámky: „Vingegaard (double 🩷💛)"
- Někteří píší **PŘÍJMENÍ Jméno** velkými (Tipujici_52), jiní `J. Philipsen`

## Pravidla jarní série klasik

Adam_WLRM je vyhlásil **25. 2. 2026** v kanálu — jediné místo, kde jsou
pravidla napsaná (jinak se vyhlašují v podcastu):

1. **Přiřazení k závodu podle data.** Tip bez označení patří k nejbližším
   nadcházejícím závodům. Kdo tipuje dopředu, musí závod pojmenovat.
2. **Zákaz editace.** Tip s poznámkou „(upraveno)" se **nepočítá**.
   Gramatické chyby se promíjejí, editace ne.
   Potvrzeno uživatelem 25. 9. 2026 — platí i do budoucna.
   Při přepisu do `tipy.csv` takový tip **vynechat úplně**, ne jen označit.
3. **Uzávěrka** je vždy před oficiálním startem závodu.
4. Série má **9 závodů**: Omloop, Kuurne, Strade Bianche, Milán–San Remo,
   Ronde, Roubaix, Amstel, Valonský šíp, LBL.

**Ženy:** do 25. 3. 2026 se počítaly, od 10. 4. 2026 už ne
(*„Pokojne tipujte aj zeny, ale do sutaze sa pocitaju iba muzi"*).

**Rozstřel při shodě bodů** rozhoduje podle umístění i nebodovaných tipů
(Adam k MSR: Tipujici_58 vyhrála nad dodosaurem, protože „trafila vyssie
umiestnenie nebodovaneho zvysku").

## Pravidla pro sporné případy

Potvrzeno uživatelem 25. 9. 2026:

**Chybějící kategorie** — když někdo něco nevyplní (Päter neměl na Vueltě
Peňas Blancas), není to chyba. Za tu kategorii prostě nedostane body.
Nedopisovat, nehádat.

**Tip po uzávěrce** — platí, pokud ho pořadatel pustil do hry. Tipujici_49
poslala tip na Giro 10 minut po uzavření a Adam_WLRM ji výslovně nechal
soutěžit. Takový tip se počítá.

**Nejasný tip** — nehádat. Vypsat uživateli **od koho** a **kdy** byl
publikován a co je nejasné; on rozhodne. Do `ZDROJ_zpravy.txt` pak zapsat
`VYRESENO (uzivatel <datum>): ...`, ať se stejná otázka neopakuje.

## Formáty zápisu tipů

Čtyři základní vzory:

1. **Textové hlavičky** — `ITT W: 1. Reusser 2. Vollering 3. Noojien`
2. **Emoji místo čísel** — `🥇 Pogačar / 🥈 Gall / 🥉 Onley`
3. **Čárkami oddělený seznam** bez čísel — `Pogačar,Gall,Carapaz,`
   (pořadí je dané pozicí)
4. **Kombinace** — hlavička textem, pořadí emoji

Velmi časté je, že **první tři jména na začátku zprávy bez popisku**
jsou GC nebo hlavní kategorie.

## Poznámky k soutěži

Vyhodnocení dělá ručně **Adam_WLRM**. Po Tour 2026 sám přiznal chybu
(28. 7. 2026): *„Ja som tam proste videl pri vyhodnocovani svojimi
poloslepymi ocami Pagacara"* — místo Carapaze v kategorii 30+.

Pravidla se vyhlašují **v podcastu, ne v kanálu**. Z dat jde odvodit
struktura (kolik kategorií, kolik míst), ale **ne bodování** — to se musí
zeptat uživatele.
