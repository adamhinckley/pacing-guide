# Old Testament Seminary pacing guide

A phone-friendly page for the Fall 2026 4-day Old Testament seminary schedule. It shows **the previous week and all upcoming class days**, and each lesson opens the matching page in the [Old Testament Seminary Teacher Manual](https://www.churchofjesuschrist.org/study/manual/old-testament-seminary-manual-2026?lang=eng).

Open [index.html](index.html) in a browser, or enable GitHub Pages on this repository and visit the published site.

## Add to Home Screen

The navy-and-gold book icon is included so the page looks like a small app on a phone.

**iPhone:** open the page in Safari → Share → **Add to Home Screen**.

**Android:** open the page in Chrome → menu → **Add to Home screen** / **Install app**.

## Updating the schedule

1. Edit `data/pacing-guide.csv`.
2. Run `python3 scripts/build-pacing-data.py`.
3. Refresh `index.html`.

Dates older than a week are hidden automatically, using the device’s local calendar date. Upcoming class days stay visible.
