(function (global) {
  function parseDate(iso) {
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  function stampFromDate(dt) {
    const y = dt.getFullYear();
    const m = String(dt.getMonth() + 1).padStart(2, "0");
    const d = String(dt.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  function addDays(iso, days) {
    const dt = parseDate(iso);
    dt.setDate(dt.getDate() + days);
    return stampFromDate(dt);
  }

  function weeksWithDays(weeks, predicate) {
    return (weeks || []).map((week) => ({
      ...week,
      days: week.days.filter(predicate)
    })).filter((week) => week.days.length);
  }

  function upcomingWeeks(weeks, today) {
    return weeksWithDays(weeks, (day) => day.date >= today);
  }

  function previousWeeks(weeks, today) {
    return weeksWithDays(weeks, (day) => day.date < today);
  }

  function withLang(url) {
    if (!url) return url;
    if (/[?&]lang=/.test(url)) return url;
    return url + (url.includes("?") ? "&" : "?") + "lang=eng";
  }

  function lessonUrl(url, options) {
    const web = withLang(url);
    const toApp = Boolean(options && (options.standalone || options.ios));
    if (toApp && web.startsWith("https://www.churchofjesuschrist.org/study")) {
      return web.replace("https://www.churchofjesuschrist.org/study", "gospellibrary://content");
    }
    return web;
  }

  function lessonEntries(lesson) {
    const teacher = {
      number: lesson.number,
      title: lesson.title,
      fullTitle: lesson.fullTitle,
      url: lesson.url,
      kind: lesson.kind,
      audience: "teacher"
    };
    if (!lesson.student) return [teacher];
    return [
      teacher,
      {
        number: lesson.student.number,
        title: lesson.student.title,
        fullTitle: lesson.student.fullTitle,
        url: lesson.student.url,
        kind: lesson.student.kind,
        audience: "student"
      }
    ];
  }

  global.PacingLib = {
    parseDate,
    stampFromDate,
    addDays,
    upcomingWeeks,
    previousWeeks,
    withLang,
    lessonUrl,
    lessonEntries
  };
})(typeof window !== "undefined" ? window : globalThis);
