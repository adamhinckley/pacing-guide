#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..");
const context = { window: {}, console };
context.window = context;
context.globalThis = context;
vm.runInNewContext(fs.readFileSync(path.join(root, "pacing-lib.js"), "utf8"), context);
vm.runInNewContext(fs.readFileSync(path.join(root, "pacing-data.js"), "utf8"), context);

const { visibleWeeks, addDays, withLang, lessonUrl } = context.PacingLib;
const weeks = context.PACING.weeks;
const today = "2026-08-18";
const visible = visibleWeeks(weeks, today);
const dates = visible.flatMap((week) => week.days.map((day) => day.date));

assert.ok(dates.includes("2026-08-11"), "keep lessons from the previous week");
assert.ok(dates.includes(today), "keep today’s lesson");
assert.ok(dates.includes("2026-08-19"), "keep tomorrow’s lesson");
assert.ok(dates.includes("2026-12-17"), "keep the last future class day");
assert.ok(!dates.includes("2026-08-10"), "hide lessons older than one week");
assert.equal(addDays(today, -7), "2026-08-11");

const later = visibleWeeks(weeks, "2026-09-01");
const laterDates = later.flatMap((week) => week.days.map((day) => day.date));
assert.ok(!laterDates.includes("2026-08-18"), "from Sept 1, hide lessons older than one week");
assert.ok(laterDates.includes("2026-08-25"), "from Sept 1, keep the previous week");
assert.ok(laterDates.includes("2026-12-17"), "from Sept 1, keep later future lessons");

const web = "https://www.churchofjesuschrist.org/study/manual/old-testament-seminary-manual-2026/33-psalms-1-46/333-psalm-23";
assert.equal(withLang(web), web + "?lang=eng");
assert.equal(withLang(web + "?lang=eng"), web + "?lang=eng");
assert.equal(
  lessonUrl(web, { standalone: true }),
  "gospellibrary://content/manual/old-testament-seminary-manual-2026/33-psalms-1-46/333-psalm-23?lang=eng"
);
assert.equal(
  lessonUrl(web, { ios: true }),
  "gospellibrary://content/manual/old-testament-seminary-manual-2026/33-psalms-1-46/333-psalm-23?lang=eng"
);
assert.equal(lessonUrl(web + "?lang=eng"), web + "?lang=eng");

const lessonHrefs = visible.flatMap((week) =>
  week.days.flatMap((day) => day.lessons.map((lesson) => lesson.url))
);
assert.ok(lessonHrefs.length > 0, "visible days should still have lesson URLs");
for (const href of lessonHrefs) {
  assert.match(
    href,
    /^https:\/\/www\.churchofjesuschrist\.org\/study\/manual\/old-testament-seminary-manual-2026\//,
    `unexpected lesson URL: ${href}`
  );
  assert.ok(href.includes("?lang=eng"), `lesson URL missing lang: ${href}`);
}

console.log(`ok: ${dates.length} visible class days from ${dates[0]} to ${dates[dates.length - 1]}`);
