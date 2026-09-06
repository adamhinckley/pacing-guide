# Old Testament Seminary pacing guide

A phone-friendly page for the Fall 2026 4-day Old Testament seminary schedule. It opens on **today’s lesson** and the rest of the year. Earlier class days are under **Previous lessons**. Each lesson opens the matching page in the [Old Testament Seminary Teacher Manual](https://www.churchofjesuschrist.org/study/manual/old-testament-seminary-manual-2026?lang=eng).

Open [index.html](index.html) in a browser, or enable GitHub Pages on this repository and visit the published site.

## Add to Home Screen

The navy-and-gold book icon is included so the page looks like a small app on a phone.

**iPhone:** open the page in Safari → Share → **Add to Home Screen**.

**Android:** open the page in Chrome → menu → **Add to Home screen** / **Install app**.

## Updating the schedule

1. Edit `data/pacing-guide.csv`.
2. Run `python3 scripts/build-pacing-data.py`.
3. Refresh `index.html`.

The build also refreshes `version.json`, which home-screen installs use to detect new deploys. After editing `index.html` or other static files without rebuilding the schedule, run `python3 scripts/stamp_version.py`.

The default view starts at the device’s local calendar date. Earlier class days stay available under Previous lessons.

## Home screen updates

iPhone and iPad **Add to Home Screen** apps cache the page aggressively, so a new GitHub Pages deploy can look stale until the phone reloads.

This site uses a network-first service worker plus a `version.json` check so the home-screen app picks up published changes when it is opened again (or brought back to the foreground) while online.

If an install is still stuck on an older build after this update ships, delete the home-screen icon once, open the site in Safari, then add it to the Home Screen again.
