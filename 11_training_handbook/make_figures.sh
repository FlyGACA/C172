#!/bin/sh
# The two labelled illustrations (S-4 exterior, S-3 flight controls) exist as print-master PDFs only. A browser cannot show a PDF
# in an <img>, so rasterise them (300 dpi) for the handbook page: the page then carries the labelled figure, not the bare render.
# Rebuild after `npm run figures`. Needs pdftoppm (poppler).
set -eu
cd "$(dirname "$0")/.."
for id in aircraft-exterior flight-controls; do
  for lang in en ar; do
    pdftoppm -png -r 300 -singlefile "09_book_figures/out/$lang/$id.pdf" "11_training_handbook/figures/$id.$lang"
  done
done
