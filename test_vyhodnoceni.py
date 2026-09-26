r"""
Testy vyhodnocovaciho skriptu.

Pouziti:
    python test_vyhodnoceni.py

Overuje na vymyslenych datech, ze bodovani pocita spravne. Pusta se to
po kazde zmene vyhodnoceni.py nebo aliasy.csv - hlavne po rozsireni
aliasu, kde hrozi, ze prilis kratky vzor zacne chytat jina jmena.

Kazdy test rekne, co ocekava a co dostal. Na konci je souhrn.
"""

import csv
import os
import shutil
import subprocess
import sys
import tempfile

KOREN = os.path.dirname(os.path.abspath(__file__))
SKRIPT = os.path.join(KOREN, "vyhodnoceni.py")
ALIASY = os.path.join(KOREN, "aliasy.csv")


def zapis(cesta, radky):
    with open(cesta, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, delimiter=";").writerows(radky)


def spust(kategorie, vysledky, tipy):
    """Vytvori docasnou soutez, spusti skript a vrati {prezdivka: body}."""
    slozka = tempfile.mkdtemp(prefix="test_tipovacka_")
    try:
        zapis(os.path.join(slozka, "kategorie.csv"), kategorie)
        zapis(os.path.join(slozka, "skutecne_vysledky.csv"), vysledky)
        zapis(os.path.join(slozka, "tipy.csv"), tipy)
        if os.path.exists(ALIASY):
            shutil.copyfile(ALIASY, os.path.join(slozka, "aliasy.csv"))

        subprocess.run([sys.executable, SKRIPT, slozka],
                       capture_output=True, check=True)

        vystup = os.path.join(slozka, "vyhodnoceni_souteze.csv")
        if not os.path.exists(vystup):
            return {}
        with open(vystup, encoding="utf-8-sig", newline="") as f:
            return {r["prezdivka"]: int(r["body"])
                    for r in csv.DictReader(f, delimiter=";")}
    finally:
        shutil.rmtree(slozka, ignore_errors=True)


HLAVICKA_TIPY = ["datum", "cas", "tipujici", "kategorie", "poradi",
                 "tip_raw", "tip_kanonicky"]


def tip(kdo, kat, por, raw, kanon):
    return ["2026-01-01", "10:00", kdo, kat, str(por), raw, kanon]


def test_bodovani():
    """Podium: 50/30/20, na podiu jinde 10. Jeden: 30 za trefu."""
    kategorie = [
        ["kategorie", "typ", "body_1", "body_2", "body_3", "body_jinde",
         "zdroj", "popis"],
        ["GC", "podium", "50", "30", "20", "10", "test", ""],
        ["Vrchar", "jeden", "30", "", "", "", "test", ""],
    ]
    vysledky = [["kategorie", "poradi", "jezdec"],
                ["GC", "1", "Pogacar"], ["GC", "2", "Gall"],
                ["GC", "3", "Kuss"], ["Vrchar", "1", "Carapaz"]]
    tipy = [HLAVICKA_TIPY,
        # vsechno spravne
        tip("Vse", "GC", 1, "Pogacar", "Pogacar Tadej"),
        tip("Vse", "GC", 2, "Gall", "Gall Felix"),
        tip("Vse", "GC", 3, "Kuss", "Kuss Sepp"),
        tip("Vse", "Vrchar", 1, "Carapaz", "Carapaz Richard"),
        # spravna trojice, spatne poradi
        tip("Prohozene", "GC", 1, "Gall", "Gall Felix"),
        tip("Prohozene", "GC", 2, "Kuss", "Kuss Sepp"),
        tip("Prohozene", "GC", 3, "Pogacar", "Pogacar Tadej"),
        # u typu 'jeden' se 'na podiu jinde' NEUPLATNUJE
        tip("Prohozene", "Vrchar", 1, "Pogacar", "Pogacar Tadej"),
        # chybejici kategorie = zadne body, ne chyba
        tip("BezVrchare", "GC", 1, "Pogacar", "Pogacar Tadej"),
        # nic netrefil
        tip("Nic", "GC", 1, "Landa", "Landa Mikel"),
    ]
    return spust(kategorie, vysledky, tipy), {
        "Vse": 130,          # 50+30+20 + 30
        "Prohozene": 30,     # 10+10+10, vrchar 0
        "BezVrchare": 50,    # jen 1. misto
        "Nic": 0,
    }


def test_parovani_jmen():
    """Prezdivky a diakritika se musi spojit, ruzna jmena ne."""
    kategorie = [
        ["kategorie", "typ", "body_1", "body_2", "body_3", "body_jinde",
         "zdroj", "popis"],
        ["GC", "podium", "50", "30", "20", "10", "test", ""],
    ]
    vysledky = [["kategorie", "poradi", "jezdec"],
                ["GC", "1", "Pogacar"], ["GC", "2", "Backstedt"],
                ["GC", "3", "Del Torro"]]
    tipy = [HLAVICKA_TIPY,
        # prezdivka, prehlaska, preklep v prijmeni
        tip("Varianty", "GC", 1, "Pogi", "Pogacar Tadej"),
        tip("Varianty", "GC", 2, "Bäckstedt", "Bäckstedt Zoe"),
        tip("Varianty", "GC", 3, "Torito", "Del Toro Isaac"),
        # jina jmena, ktera se nesmi chytit
        tip("Jini", "GC", 1, "Torres", "Torres Pablo"),
        tip("Jini", "GC", 2, "Martin", "Martin Guillaume"),
        tip("Jini", "GC", 3, "Fortunato", "Fortunato Lorenzo"),
    ]
    return spust(kategorie, vysledky, tipy), {
        "Varianty": 100,   # 50+30+20
        "Jini": 0,
    }


def test_delene_poradi():
    """Pri shode bodu sdilene poradi, nasledujici pozice se preskoci."""
    kategorie = [
        ["kategorie", "typ", "body_1", "body_2", "body_3", "body_jinde",
         "zdroj", "popis"],
        ["GC", "podium", "50", "30", "20", "10", "test", ""],
    ]
    vysledky = [["kategorie", "poradi", "jezdec"], ["GC", "1", "Pogacar"]]
    tipy = [HLAVICKA_TIPY,
        tip("Zdenek", "GC", 1, "Pogacar", "Pogacar Tadej"),
        tip("Adam", "GC", 1, "Pogacar", "Pogacar Tadej"),
        tip("Nula", "GC", 1, "Landa", "Landa Mikel"),
    ]
    body = spust(kategorie, vysledky, tipy)
    return body, {"Zdenek": 50, "Adam": 50, "Nula": 0}


def test_prubezne_poradi():
    """Nevyplnena kategorie se ignoruje - umoznuje prubezne poradi."""
    kategorie = [
        ["kategorie", "typ", "body_1", "body_2", "body_3", "body_jinde",
         "zdroj", "popis"],
        ["ITT", "podium", "50", "30", "20", "10", "test", ""],
        ["RR", "podium", "50", "30", "20", "10", "test", ""],
    ]
    # RR se jeste nejel
    vysledky = [["kategorie", "poradi", "jezdec"],
                ["ITT", "1", "Evenepoel"],
                ["RR", "1", ""], ["RR", "2", ""], ["RR", "3", ""]]
    tipy = [HLAVICKA_TIPY,
        tip("Kdo", "ITT", 1, "Remco", "Evenepoel Remco"),
        tip("Kdo", "RR", 1, "Pogacar", "Pogacar Tadej"),
    ]
    return spust(kategorie, vysledky, tipy), {"Kdo": 50}


TESTY = [
    ("bodovani podium i jeden", test_bodovani),
    ("parovani jmen", test_parovani_jmen),
    ("delene poradi a nulovi", test_delene_poradi),
    ("prubezne poradi", test_prubezne_poradi),
]


def main():
    chyb = 0
    for nazev, funkce in TESTY:
        dostal, cekal = funkce()
        potize = []
        for kdo, body in sorted(cekal.items()):
            if dostal.get(kdo) != body:
                potize.append("  %s: cekano %d, dostal %s"
                              % (kdo, body, dostal.get(kdo)))
        navic = set(dostal) - set(cekal)
        if navic:
            potize.append("  navic v tabulce: %s" % ", ".join(sorted(navic)))

        if potize:
            chyb += 1
            print("CHYBA  %s" % nazev)
            print("\n".join(potize))
        else:
            print("OK     %s" % nazev)

    print()
    if chyb:
        print("Neproslo testu: %d" % chyb)
        sys.exit(1)
    print("Vsechny testy prosly.")


if __name__ == "__main__":
    main()
