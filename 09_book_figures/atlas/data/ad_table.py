"""Rows of a named table of a saved eAIP aerodrome page (deleted text dropped, rowspans carried down).   python3 -I ad_table.py page.html AD2_18_TABLE"""
import re, sys
from html.parser import HTMLParser


class Grab(HTMLParser):
    def __init__(self, key):
        super().__init__(convert_charrefs=True)
        self.key, self.depth, self.inside, self.rows, self.row, self.cell, self.skip = key, 0, 0, [], None, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            if self.inside:
                self.inside += 1
            elif self.key in (a.get("class") or ""):
                self.inside = 1
        if not self.inside:
            return
        if tag == "span" and "deletedAIRAC" in (a.get("class") or ""):
            self.skip = 1
        elif tag == "span" and self.skip:
            self.skip += 1
        if self.inside == 1 and tag == "tr":
            self.row = []
        if self.inside == 1 and tag in ("td", "th") and self.row is not None:
            self.cell = {"rowspan": int(a.get("rowspan") or 1), "text": []}
        if tag == "br" and self.cell is not None:
            self.cell["text"].append("\n")

    def handle_endtag(self, tag):
        if not self.inside:
            return
        if tag == "span" and self.skip:
            self.skip -= 1
        if self.inside == 1 and tag in ("td", "th") and self.cell is not None:
            lines = [re.sub(r"\s+", " ", l).strip() for l in "".join(self.cell["text"]).replace("\xa0", " ").split("\n")]
            self.row.append((self.cell["rowspan"], [l for l in lines if l]))
            self.cell = None
        if self.inside == 1 and tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        if tag == "table":
            self.inside -= 1

    def handle_data(self, data):
        if self.inside and self.cell is not None and not self.skip:
            self.cell["text"].append(data)


def table(path, key):
    g = Grab(key)
    g.feed(open(path, encoding="utf-8", errors="replace").read())
    return g.rows


if __name__ == "__main__":
    for r in table(sys.argv[1], sys.argv[2])[:40]:
        print(r)
