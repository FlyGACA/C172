# Aerodrome atlas: the cards

> [!NOTE]
> Superseded. The atlas moved to [FlyGACA/airport](https://github.com/FlyGACA/airport) on 17 November 2026 and is maintained there (one AIP edition per facts file, Arabic edition, diagrams and plates). This folder is the first batch, built from AMDT 11/26, kept as a record; change the atlas there, not here.

A first batch (all 29 cards; `out/sheet-all.jpg` shows them together) for a separate book, the FlyGACA aerodrome atlas: one card for each civil aerodrome of the Kingdom, with what its entry AD 2 in AIP-KSA prints, on an open satellite picture. An editorial draft; nothing here is approved or verified, and nothing is for navigation. Fly GACA is independent and is not affiliated with GACA. (FlyGACA جهة مستقلة وليست تابعة للهيئة العامة للطيران المدني.)

## Decisions of the owner (17 November 2026)

- One card for each aerodrome ("an AD card"), the civil aerodromes first: the 28 that AD 1.3 lists with scheduled traffic, and Thumamah.
- The atlas is a book of its own, sold on its own; the handbook may borrow from it.
- The copyright notice of the AIP (GEN 0.1.5 asks for GACA's prior agreement to redistribution and copying of its contents) is the owner's to settle. Until it is settled, nothing here is described as cleared for publication.

## What is here

| File | What it is |
| --- | --- |
| `data/build_atlas_facts.py` | Builds `data/atlas_facts.json` from the official AD 2 pages of AIRAC AIP AMDT 11/26 (AD 2.2 and AD 2.18 read from the page; runways and airspace taken from the `saudi-airspace` repository and each value looked for in the page) |
| `data/ad_table.py` | Reads a named table of an eAIP page, with row spans, leaving out what an amendment marks as deleted |
| `data/atlas_facts.json` | The 29 aerodromes, values as printed, with the hash of each page and the count of values found on it |
| `data/fetch_atlas_open.py` | Fetches an open Sentinel-2 picture of each aerodrome (needs `rasterio` and network access) |
| `data/open/` | The pictures and what describes them. Attribution, required by the licence: "Contains modified Copernicus Sentinel data 2026" |
| `card.py`, `rasterize_cards.mjs` | Draw the cards (`cache/<icao>.svg`) and flatten them (`out/card-<icao>.jpg`) |

## Known gaps of the pilot

- The pages of AMDT 11/26 are not kept here; `build_atlas_facts.py` takes their folder as an argument.
- Two values of the repository's data are not on the AMDT 11/26 page (the ASDA of Rafha's runways) and are flagged in the facts file.
- AD 2.18 on a card: one row for each call sign, with its first VHF frequency and "+N" for the others; where the block has no room for every call sign, the service with the most call signs becomes one row under the call sign printed first (Jeddah, Riyadh). The designations ATS (Um Almelh) and SMGCS (Al Jouf) are shown as printed.
- Al Qaisumah, Rabigh and Arar print NIL in every column of AD 2.18 on the AMDT 11/26 pages; their cards show NIL, as printed. Not checked against any other source.
- Five pictures (Rabigh, Arar, Red Sea, Al Jouf, Yenbo) are joined from the scenes of more than one tile or pass (`ATLAS_MOSAIC=1`); a seam may show.
- The ground of every card is brought to one range of lightness, and very strong colour is drawn in (`tone()` in `card.py`): the pictures are for orientation, not true colour.
- No Arabic edition yet, no text beside the cards, no book around them.
