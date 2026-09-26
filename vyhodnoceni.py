# -*- coding: utf-8 -*-
r"""
Vyhodnoceni tipovaci souteze - obecne, pro libovolny zavod nebo serii.

Pouziti:
    python vyhodnoceni.py                        # data v teto slozce
    python vyhodnoceni.py souteze/vuelta-2026    # data v podslozce

Cte tipy.csv a skutecne_vysledky.csv, vypise poradi tipujicich a ulozi
ho do vyhodnoceni_souteze.csv.

Kategorie nejsou nijak pevne dane. Kdyz ve slozce lezi kategorie.csv,
precte si z nej typ kategorie a bodovani:

    kategorie;typ;body_1;body_2;body_3;body_jinde;zdroj;popis
    GC;podium;50;30;20;10;...;Celkove poradi
    Vrchar;jeden;30;;;;...;Puntikovany dres

    typ podium - tipuji se 3 mista, boduje se i zavodnik na podiu na
                 jinem miste (body_jinde)
    typ jeden  - tipuje se jediny vitez (dres, tym), body jen za trefu

Bez kategorie.csv plati vychozi podiove bodovani 50/30/20/10 podle
konstant nize.

Funguje i pro prubezne poradi: staci vyplnit jen ty kategorie, ktere uz
probehly. Nevyplnene se ignoruji.
"""

import csv
import os
import sys
import unicodedata
from collections import defaultdict

KOREN = os.path.dirname(os.path.abspath(__file__))

# Slozku souteze lze zadat argumentem:
#     python vyhodnoceni.py souteze/vuelta-2026
# Bez argumentu se pracuje primo v korenove slozce.
SLOZKA = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else KOREN

SOUBOR_TIPY = os.path.join(SLOZKA, "tipy.csv")
SOUBOR_VYSLEDKY = os.path.join(SLOZKA, "skutecne_vysledky.csv")
SOUBOR_VYSTUP = os.path.join(SLOZKA, "vyhodnoceni_souteze.csv")
SOUBOR_KATEGORIE = os.path.join(SLOZKA, "kategorie.csv")

# Aliasy jsou spolecne pro vsechny souteze - hledaji se v korenove slozce,
# a kdyz je ma soutez vlastni, ma prednost jeji soubor.
SOUBOR_ALIASY = os.path.join(SLOZKA, "aliasy.csv")
if not os.path.exists(SOUBOR_ALIASY):
    SOUBOR_ALIASY = os.path.join(KOREN, "aliasy.csv")

# Bodovani. Klic je tipovane misto, hodnota pocet bodu za presny zasah.
# Pro podium se tipuji tri mista; pro jinou soutez staci upravit tady.
BODY_ZA_MISTO = {"1": 50, "2": 30, "3": 20}
BODY_PODIUM_JINDE = 10


def nacti_aliasy():
    """
    Nacte viceslovna prijmeni a jejich varianty z aliasy.csv.

    Format: dva sloupce oddelene strednikem - hledany vzor a kanonicky tvar,
    oba malymi pismeny bez diakritiky. Radek zacinajici # je komentar.
    Kdyz soubor neexistuje, pouziji se jen jednoslovna prijmeni.
    """
    if not os.path.exists(SOUBOR_ALIASY):
        return ()
    aliasy = []
    with open(SOUBOR_ALIASY, encoding="utf-8-sig", newline="") as f:
        for radek in csv.reader(f, delimiter=";"):
            if not radek or radek[0].strip().startswith("#"):
                continue
            if len(radek) >= 2 and radek[0].strip():
                aliasy.append((radek[0].strip().lower(),
                               radek[1].strip().lower()))
    return tuple(aliasy)


ALIASY = nacti_aliasy()


def bez_diakritiky(text):
    """Odstrani diakritiku: 'Backstedt' a 'Backstedt' maji dat stejny klic."""
    rozlozene = unicodedata.normalize("NFD", text)
    return "".join(z for z in rozlozene if unicodedata.category(z) != "Mn")


def klic(jmeno):
    """Prevede jmeno jezdce na porovnatelny tvar (prijmeni, mala pismena)."""
    j = (jmeno or "").strip()
    nizke = bez_diakritiky(j.lower())
    for vzor, kanon in ALIASY:
        if nizke.startswith(vzor) or vzor in nizke:
            return kanon
    # tip_kanonicky ma tvar "Prijmeni Jmeno" -> bereme prvni slovo
    return nizke.split(" ")[0] if j else ""


def nacti_csv(cesta):
    with open(cesta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def nacti_kategorie():
    """
    Nacte kategorie.csv: typ kategorie a bodovani.

    Kdyz soubor chybi, pouzije se vychozi podiove bodovani pro vsechny
    kategorie, ktere se objevi v datech (zpetna kompatibilita).
    """
    if not os.path.exists(SOUBOR_KATEGORIE):
        return {}
    kategorie = {}
    for r in nacti_csv(SOUBOR_KATEGORIE):
        nazev = (r.get("kategorie") or "").strip()
        if not nazev:
            continue

        def cislo(klic_sloupce):
            h = (r.get(klic_sloupce) or "").strip()
            return int(h) if h.isdigit() else 0

        kategorie[nazev] = {
            "typ": (r.get("typ") or "podium").strip(),
            "body": {"1": cislo("body_1"),
                     "2": cislo("body_2"),
                     "3": cislo("body_3")},
            "body_jinde": cislo("body_jinde"),
        }
    return kategorie


def pravidla_kategorie(kategorie, nazev):
    """Vrati bodovani dane kategorie, nebo vychozi podiove."""
    if nazev in kategorie:
        return kategorie[nazev]
    return {"typ": "podium",
            "body": dict(BODY_ZA_MISTO),
            "body_jinde": BODY_PODIUM_JINDE}


def main():
    tipy = nacti_csv(SOUBOR_TIPY)
    vysledky_radky = nacti_csv(SOUBOR_VYSLEDKY)
    kategorie = nacti_kategorie()

    vysledky = defaultdict(dict)       # [kategorie][poradi] = klic zavodnika
    podium = defaultdict(set)          # [kategorie] = {klice na podiu}
    for r in vysledky_radky:
        jezdec = (r.get("jezdec") or "").strip()
        if not jezdec:
            continue
        kat, por = r["kategorie"].strip(), r["poradi"].strip()
        vysledky[kat][por] = klic(jezdec)
        podium[kat].add(klic(jezdec))

    if not vysledky:
        print("Soubor skutecne_vysledky.csv je zatim prazdny.")
        print("Vypln sloupec 'jezdec' a spust skript znovu.")
        return

    # Kazdy, kdo tipoval, ma byt ve vysledne tabulce - i kdyby mel 0 bodu.
    body = defaultdict(int)
    for t in tipy:
        body[t["tipujici"].strip()] += 0

    for t in tipy:
        kat, por = t["kategorie"].strip(), t["poradi"].strip()
        if kat not in vysledky:
            continue
        pravidla = pravidla_kategorie(kategorie, kat)
        tip = klic(t["tip_kanonicky"])
        kdo = t["tipujici"].strip()

        if pravidla["typ"] == "jeden":
            # Jediny tip (dres, tym): body jen za presnou trefu.
            if vysledky[kat].get("1") == tip:
                body[kdo] += pravidla["body"]["1"]
        elif vysledky[kat].get(por) == tip:
            body[kdo] += pravidla["body"].get(por, 0)
        elif tip in podium[kat]:
            body[kdo] += pravidla["body_jinde"]

    # Primarne podle bodu sestupne, pri shode abecedne podle prezdivky.
    serazeno = sorted(body.items(), key=lambda x: (-x[1], x[0].lower()))

    # Delene poradi pri shode bodu.
    radky, predchozi_body, poradi = [], None, 0
    for i, (kdo, b) in enumerate(serazeno, 1):
        if b != predchozi_body:
            poradi, predchozi_body = i, b
        radky.append((poradi, kdo, b))

    print()
    print(f"{'#':<5}{'prezdivka':<20}{'body':>6}")
    print("-" * 31)
    for p, kdo, b in radky:
        print(f"{p:<5}{kdo:<20}{b:>6}")

    with open(SOUBOR_VYSTUP, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["poradi", "prezdivka", "body"])
        w.writerows(radky)

    print(f"\nUlozeno do: {SOUBOR_VYSTUP}")


if __name__ == "__main__":
    main()
