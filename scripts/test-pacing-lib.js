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

const { upcomingWeeks, previousWeeks, addDays, withLang, lessonUrl } = context.PacingLib;
const weeks = context.PACING.weeks;
const today = "2026-08-18";
const upcoming = upcomingWeeks(weeks, today);
const previous = previousWeeks(weeks, today);
const upcomingDates = upcoming.flatMap((week) => week.days.map((day) => day.date));
const previousDates = previous.flatMap((week) => week.days.map((day) => day.date));

assert.ok(upcomingDates.includes(today), "keep today’s lesson in the default view");
assert.ok(upcomingDates.includes("2026-08-19"), "keep tomorrow’s lesson");
assert.ok(upcomingDates.includes("2026-12-17"), "keep the last future class day");
assert.ok(!upcomingDates.includes("2026-08-17"), "hide yesterday from the default view");
assert.ok(previousDates.includes("2026-08-17"), "keep yesterday in previous lessons");
assert.ok(previousDates.includes("2026-08-10"), "keep the first class day in previous lessons");
assert.ok(!previousDates.includes(today), "do not repeat today in previous lessons");
assert.equal(previousDates[0], "2026-08-10", "keep previous lessons in calendar order");
assert.equal(addDays(today, -7), "2026-08-11");

const midweekUpcoming = upcomingWeeks(weeks, "2026-08-26");
const midweekPrevious = previousWeeks(weeks, "2026-08-26");
const midweekUpcomingDates = midweekUpcoming.flatMap((week) => week.days.map((day) => day.date));
const midweekPreviousDates = midweekPrevious.flatMap((week) => week.days.map((day) => day.date));
assert.ok(midweekUpcomingDates.includes("2026-08-26"), "from Wednesday, keep that day’s lesson");
assert.ok(!midweekUpcomingDates.includes("2026-08-25"), "from Wednesday, hide Tuesday");
assert.ok(midweekPreviousDates.includes("2026-08-25"), "from Wednesday, Tuesday is previous");
assert.ok(midweekPreviousDates.includes("2026-08-24"), "from Wednesday, Monday is previous");

const laterUpcoming = upcomingWeeks(weeks, "2026-09-01");
const laterPrevious = previousWeeks(weeks, "2026-09-01");
const laterUpcomingDates = laterUpcoming.flatMap((week) => week.days.map((day) => day.date));
const laterPreviousDates = laterPrevious.flatMap((week) => week.days.map((day) => day.date));
assert.ok(!laterUpcomingDates.includes("2026-08-18"), "from Sept 1, hide August from the default view");
assert.ok(laterPreviousDates.includes("2026-08-18"), "from Sept 1, August is in previous lessons");
assert.ok(laterUpcomingDates.includes("2026-12-17"), "from Sept 1, keep later future lessons");

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

const lessonHrefs = upcoming.flatMap((week) =>
  week.days.flatMap((day) => day.lessons.map((lesson) => lesson.url))
);
assert.ok(lessonHrefs.length > 0, "upcoming days should still have lesson URLs");
for (const href of lessonHrefs) {
  assert.match(
    href,
    /^https:\/\/www.churchofjesuschrist.org\/study\/manual\/old-testament-seminary-manual-2026\//,
    `unexpected lesson URL: ${href}`
  );
  assert.ok(href.includes("?lang=eng"), `lesson URL missing lang: ${href}`);
}

console.log(`ok: ${upcomingDates.length} upcoming class days from ${upcomingDates[0]} to ${upcomingDates[upcomingDates.length - 1]}; ${previousDates.length} previous`);
