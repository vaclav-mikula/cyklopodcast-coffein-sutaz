# -*- coding: utf-8 -*-
r"""
Vyhodnoceni tipovaci souteze - obecne, pro libovolny zavod nebo serii.

Pouziti:
    python vyhodnoceni.py

Cte tipy.csv a skutecne_vysledky.csv (oba ve stejne slozce), vypise
poradi tipujicich a ulozi ho do vyhodnoceni_souteze.csv.

Kategorie nejsou nijak pevne dane - skript si je precte z dat. Muze jit
o ctyri zavody mistrovstvi sveta, etapy Grand Tour, jarni klasiky nebo
cokoliv jineho; staci pouzivat stejne nazvy kategorii v obou souborech.

Funguje i pro prubezne poradi: staci vyplnit jen ty kategorie, ktere uz
probehly. Nevyplnene se ignoruji.

Bodovani (viz konstanty nize):
    50 b. - uhodnute 1. misto
    30 b. - uhodnute 2. misto
    20 b. - uhodnute 3. misto
    10 b. - zavodnik je na podiu dane kategorie, ale na jinem miste
"""

import csv
import os
import unicodedata
from collections import defaultdict

SLOZKA = os.path.dirname(os.path.abspath(__file__))
SOUBOR_TIPY = os.path.join(SLOZKA, "tipy.csv")
SOUBOR_VYSLEDKY = os.path.join(SLOZKA, "skutecne_vysledky.csv")
SOUBOR_VYSTUP = os.path.join(SLOZKA, "vyhodnoceni_souteze.csv")
SOUBOR_ALIASY = os.path.join(SLOZKA, "aliasy.csv")

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


def main():
    tipy = nacti_csv(SOUBOR_TIPY)
    vysledky_radky = nacti_csv(SOUBOR_VYSLEDKY)

    vysledky = defaultdict(dict)       # [kategorie][poradi] = klic jezdce
    podium = defaultdict(set)          # [kategorie] = {klice jezdcu na podiu}
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
        tip = klic(t["tip_kanonicky"])
        if vysledky[kat].get(por) == tip:
            body[t["tipujici"].strip()] += BODY_ZA_MISTO.get(por, 0)
        elif tip in podium[kat]:
            body[t["tipujici"].strip()] += BODY_PODIUM_JINDE

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
