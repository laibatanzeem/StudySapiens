/* ==========================================================================
   StudySapiens · main.js
   Navigation, search, tabs, accordions, quiz engine, MDCAT calculator,
   filters, forms (newsletter/contact server-side with mailto fallback),
   GTM event tracking, reveals, share. Dependency-free vanilla JS.
   ========================================================================== */

/* Analytics: push an event into the GTM dataLayer (GTM snippet lives in <head>).
   Events fired: newsletter_signup, contact_submit, pdf_download,
   calculator_use, quiz_start, quiz_complete. */
function ssTrack(name, params) {
  try {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: name }, params || {}));
  } catch (err) { /* tracking must never break the page */ }
}

(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));
  const ROOT = window.SITE_ROOT || "";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- Header state / back-to-top / progress ---------------- */
  const header = $("#site-header");
  const toTop = $("#backToTop");
  const progress = $("#readProgress");
  function onScroll() {
    const y = window.scrollY;
    if (header) header.classList.toggle("scrolled", y > 12);
    if (toTop) toTop.classList.toggle("show", y > 600);
    if (progress) {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      progress.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" }));

  /* ---------------- Mobile drawer ---------------- */
  const drawer = $("#drawer");
  const openDrawer = () => { if (drawer) { drawer.classList.add("open"); document.body.style.overflow = "hidden"; } };
  const closeDrawer = () => { if (drawer) { drawer.classList.remove("open"); document.body.style.overflow = ""; } };
  $$("[data-open-drawer]").forEach(b => b.addEventListener("click", openDrawer));
  $$("[data-close-drawer]").forEach(b => b.addEventListener("click", closeDrawer));
  if (drawer) $(".drawer-bg", drawer).addEventListener("click", closeDrawer);
  $$(".drawer .d-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const sub = btn.nextElementSibling;
      const open = sub.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      const c = $(".caret", btn); if (c) c.style.transform = open ? "rotate(180deg)" : "";
    });
  });

  /* ---------------- Mega menu (touch support) ---------------- */
  $$(".has-mega > .nav-btn").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      const li = btn.parentElement;
      const wasOpen = li.classList.contains("nav-item-open");
      $$(".main-nav > li.nav-item-open").forEach(x => x.classList.remove("nav-item-open"));
      li.classList.toggle("nav-item-open", !wasOpen);
    });
  });
  document.addEventListener("click", e => {
    if (!e.target.closest(".has-mega")) $$(".main-nav > li.nav-item-open").forEach(x => x.classList.remove("nav-item-open"));
  });

  /* ---------------- Search ---------------- */
  const overlay = $("#searchOverlay");
  const sInput = $("#search-input");
  const sResults = $("#search-results");
  let sIndex = null, sFocus = -1;
  async function loadIndex() {
    if (sIndex) return sIndex;
    try { const r = await fetch(ROOT + "search.json"); sIndex = await r.json(); }
    catch (e) { sIndex = []; }
    return sIndex;
  }
  function openSearch() {
    if (!overlay) return;
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";
    sInput.value = ""; renderSearch("");
    setTimeout(() => sInput.focus(), 60);
    loadIndex().then(() => renderSearch(sInput.value));
  }
  function closeSearch() {
    if (!overlay) return;
    overlay.classList.remove("open");
    document.body.style.overflow = "";
    sFocus = -1;
  }
  $$("[data-open-search]").forEach(b => b.addEventListener("click", openSearch));
  if (overlay) overlay.addEventListener("click", e => { if (e.target === overlay) closeSearch(); });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { closeSearch(); closeDrawer(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
    if (overlay && overlay.classList.contains("open")) {
      const items = $$(".search-hit", sResults);
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        sFocus = e.key === "ArrowDown" ? Math.min(sFocus + 1, items.length - 1) : Math.max(sFocus - 1, 0);
        items.forEach((it, i) => it.classList.toggle("focus", i === sFocus));
        items[sFocus].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter" && sFocus >= 0 && items[sFocus]) {
        window.location.href = items[sFocus].href;
      }
    }
  });
  function esc(s) { return s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function renderSearch(q) {
    if (!sResults) return;
    if (!sIndex) { sResults.innerHTML = '<div class="search-empty">Loading index…</div>'; return; }
    q = (q || "").trim().toLowerCase();
    let hits;
    if (!q) hits = sIndex.filter(e => e.pop).slice(0, 8);
    else {
      const terms = q.split(/\s+/);
      hits = sIndex.map(e => {
        const hay = (e.t + " " + e.s + " " + (e.k || "") + " " + e.c).toLowerCase();
        let score = 0;
        terms.forEach(t => { if (hay.includes(t)) score += e.t.toLowerCase().includes(t) ? 3 : 1; });
        return { e, score };
      }).filter(x => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 14).map(x => x.e);
    }
    if (!hits.length) {
      sResults.innerHTML = '<div class="search-empty">No result for "<b>' + esc(q) + '</b>".<br>Try a class, subject or chapter name, e.g. <b>9 physics</b>, <b>pairing</b>, <b>mdcat</b>.</div>';
      return;
    }
    const groups = {};
    hits.forEach(h => { (groups[h.c] = groups[h.c] || []).push(h); });
    const icons = {
      "Class": "🏫", "Subject": "📘", "Chapter": "📄", "Resource": "⭐", "Test & Tool": "🧮", "Page": "🔎", "Update": "📰"
    };
    sResults.innerHTML = Object.keys(groups).map(g =>
      '<div class="sr-group">' + (icons[g] || "📌") + " " + esc(g) + "</div>" +
      groups[g].map(h =>
        '<a class="search-hit" href="' + ROOT + h.u + '">' +
        '<span class="hit-ico"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12h16M12 4l8 8-8 8"/></svg></span>' +
        '<span><span class="hit-title">' + esc(h.t) + '</span><span class="hit-meta" style="display:block">' + esc(h.s) + "</span></span></a>"
      ).join("")
    ).join("");
    sFocus = -1;
  }
  if (sInput) sInput.addEventListener("input", () => renderSearch(sInput.value));

  /* ---------------- Reveal on scroll + counters ---------------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    });
  }, { threshold: .12 });
  $$(".reveal,.reveal-l,.reveal-r").forEach(el => io.observe(el));

  const cio = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target, target = parseFloat(el.dataset.count || "0");
      const suffix = el.dataset.suffix || "", dur = 1500, t0 = performance.now();
      function tick(t) {
        const p = Math.min((t - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString() + suffix;
        if (p < 1) requestAnimationFrame(tick);
      }
      reduced ? el.textContent = target.toLocaleString() + suffix : requestAnimationFrame(tick);
      cio.unobserve(el);
    });
  }, { threshold: .4 });
  $$("[data-count]").forEach(el => cio.observe(el));

  /* ---------------- Tabs ---------------- */
  $$(".tabs").forEach(tabs => {
    const scope = tabs.parentElement;
    $$(".tab-btn", tabs).forEach(btn => btn.addEventListener("click", () => {
      $$(".tab-btn", tabs).forEach(b => b.classList.toggle("active", b === btn));
      $$(".tab-panel", scope).forEach(p => p.classList.toggle("active", p.dataset.panel === btn.dataset.tab));
      history.replaceState(null, "", "#" + btn.dataset.tab);
    }));
    const hash = (location.hash || "").replace("#", "");
    if (hash) { const b = $('.tab-btn[data-tab="' + hash + '"]', tabs); if (b) b.click(); }
  });

  /* ---------------- Accordions (QA / FAQ) ---------------- */
  $$(".qa-head,.faq-q").forEach(head => head.addEventListener("click", () => {
    const item = head.parentElement;
    item.classList.toggle("open");
    head.setAttribute("aria-expanded", item.classList.contains("open") ? "true" : "false");
  }));
  $$("[data-expand-all]").forEach(btn => btn.addEventListener("click", () => {
    const scope = btn.closest("section, .tab-panel, body");
    const items = $$(".qa", scope);
    const open = btn.dataset.state !== "open";
    items.forEach(i => i.classList.toggle("open", open));
    btn.dataset.state = open ? "open" : "closed";
    btn.textContent = open ? "Collapse all answers" : "Expand all answers";
  }));

  /* ---------------- Quiz engine ---------------- */
  window.startQuiz = startQuiz;
  function startQuiz() {
    const shell = $("#quiz");
    if (!shell || !window.QUIZ || !window.QUIZ.length) return;
    if (window.__quizStarted) return;
    window.__quizStarted = true;
    ssTrack("quiz_start", { quiz: (window.QUIZ_META && window.QUIZ_META.slug) || "" });
    const data = window.QUIZ;
    const opts = ["A", "B", "C", "D", "E", "F"];
    let cur = 0, score = 0, answered = 0, done = false, tInt = null;
    const state = data.map(() => null);
    $("#quizStart").style.display = "none";
    $("#quizBody").style.display = "block";
    const bar = $("#quizBar"), countEl = $("#quizCount"), scoreEl = $("#quizLiveScore");
    const qWrap = $("#quizQuestions");

    // timer (optional counts up)
    const t0 = Date.now();
    const tEl = $("#quizTimer span");
    if (tEl) tInt = setInterval(() => {
      const s = Math.floor((Date.now() - t0) / 1000);
      tEl.textContent = String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
    }, 1000);

    qWrap.innerHTML = data.map((it, i) =>
      '<div class="quiz-q' + (i === 0 ? " active" : "") + '" data-q="' + i + '">' +
      "<h3><span class='q-index'>Q" + (i + 1) + ".</span>" + it.q + "</h3>" +
      '<div class="quiz-opts">' + it.opts.map((o, j) =>
        '<button class="quiz-opt" data-opt="' + j + '"><span class="opt-l">' + opts[j] + "</span><span>" + o + "</span></button>"
      ).join("") + "</div>" +
      ((it.e || it.exp) ? '<div class="quiz-expl"><b>Explanation:</b> ' + (it.e || it.exp) + "</div>" : '<div class="quiz-expl"></div>') + "</div>"
    ).join("");

    function go(i) {
      cur = i;
      $$(".quiz-q", qWrap).forEach(q => q.classList.toggle("active", +q.dataset.q === i));
      countEl.textContent = "Question " + (i + 1) + " of " + data.length;
      bar.style.width = (i / data.length) * 100 + "%";
      $("#qPrev").disabled = i === 0;
      $("#qNext").textContent = i === data.length - 1 ? "Finish ✓" : "Next →";
    }
    function pick(qEl, j) {
      const i = +qEl.dataset.q;
      if (state[i] !== null) return;
      state[i] = j; answered++;
      const correct = data[i].ans;
      $$(".quiz-opt", qEl).forEach((b, k) => {
        b.disabled = true;
        if (k === correct) b.classList.add("correct");
        else if (k === j) b.classList.add("wrong");
      });
      if (j === correct) score++;
      $(".quiz-expl", qEl).classList.add("show");
      scoreEl.textContent = "Score: " + score + "/" + answered;
      bar.style.width = (answered / data.length) * 100 + "%";
      if (answered === data.length) finish();
    }
    function finish() {
      if (done) return; done = true;
      clearInterval(tInt);
      bar.style.width = "100%";
      $$(".quiz-q", qWrap).forEach(q => q.classList.remove("active"));
      const res = $("#quizResult");
      res.classList.add("show");
      const pct = Math.round((score / data.length) * 100);
      ssTrack("quiz_complete", { quiz: (window.QUIZ_META && window.QUIZ_META.slug) || "", score: score, total: data.length, percent: pct });
      const ring = $("#scoreRingVal");
      const C = 2 * Math.PI * 64;
      ring.style.strokeDasharray = C;
      ring.style.strokeDashoffset = C;
      requestAnimationFrame(() => { ring.style.strokeDashoffset = C - (pct / 100) * C; });
      $("#scoreText").textContent = pct + "%";
      $("#scoreMsg").textContent =
        score === data.length ? "Outstanding! Full marks. Chapter mastered. 🏆" :
        pct >= 80 ? "Great job! You are almost there. Revise the wrong ones." :
        pct >= 50 ? "Good effort. Read the notes once more and retake the test." :
        "Don't worry! Study the notes & exercise, then try again. You'll get there! 💪";
      $("#scoreDetail").textContent = "You answered " + score + " out of " + data.length + " questions correctly.";
      $("#quizReviewList").innerHTML = data.map((it, i) =>
        '<div class="qa' + (state[i] === it.ans ? "" : "") + '"><div class="qa-body" style="display:block;padding:14px 18px">' +
        "<b>Q" + (i + 1) + ".</b> " + it.q + "<br>" +
        '<span style="color:#2E9E63;font-weight:700">✔ ' + it.opts[it.ans] + "</span>" +
        (state[i] !== it.ans && state[i] !== null ? ' <span style="color:#D64545;font-weight:700">✖ You chose: ' + it.opts[state[i]] + "</span>" : "") +
        (it.e ? '<br><span class="muted">' + it.e + "</span>" : "") + "</div></div>"
      ).join("");
      res.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
    }
    qWrap.addEventListener("click", e => {
      const b = e.target.closest(".quiz-opt");
      if (b) pick(b.closest(".quiz-q"), +b.dataset.opt);
    });
    $("#qNext").addEventListener("click", () => { cur < data.length - 1 ? go(cur + 1) : finish(); });
    $("#qPrev").addEventListener("click", () => { if (cur > 0) go(cur - 1); });
    $("#qRestart").addEventListener("click", () => location.reload());
    go(0);
  }

  /* ---------------- MDCAT calculator ---------------- */
  const calc = $("#mdcatCalc");
  if (calc) {
    const ids = ["matric", "fsc", "mdcat"];
    const names = { matric: "Matric (SSC)", fsc: "Intermediate (FSc / HSSC)", mdcat: "MDCAT" };
    let calcUsed = false;
    function num(id) { return parseFloat($("#" + id).value) || 0; }
    function compute() {
      let total = 0, html = "", anyInput = false, invalid = null;
      ids.forEach(k => {
        const w = parseFloat(calc.dataset["w" + k]);
        const ob = $("#" + k + "Obt"), tot = $("#" + k + "Tot");
        const o = num(k + "Obt"), t = num(k + "Tot");
        if (ob.value || tot.value) anyInput = true;
        if (o < 0 || t <= 0 || o > t) { invalid = invalid || names[k]; }
        const share = t > 0 ? (o / t) * w : 0;
        total += share;
        html += "<tr><td>" + names[k] + " <span class='muted small'>(" + w + "%)</span></td><td>" +
          (t > 0 ? share.toFixed(2) + "%" : "-") + "</td></tr>";
      });
      const C = 2 * Math.PI * 84;
      const gCircle = $(".g-val");
      gCircle.style.strokeDasharray = C;
      gCircle.style.strokeDashoffset = C - Math.min(total, 100) / 100 * C;
      $("#gaugeNum").textContent = total ? total.toFixed(2) + "%" : "0%";
      $("#gaugeBreak").innerHTML = html +
        '<tr><td style="color:#fff;font-weight:800">Aggregate</td><td style="color:var(--gold-300);font-weight:800">' + total.toFixed(2) + "%</td></tr>";
      const elig = $("#eligibility");
      const mo = num("mdcatObt"), mt = num("mdcatTot");
      elig.className = "eligibility";
      if (anyInput && !invalid && mo > 0 && mt > 0) {
        const mPct = (mo / mt) * 100;
        if (mPct >= 55) { elig.classList.add("ok"); elig.innerHTML = "✔ MDCAT score " + mPct.toFixed(1) + "%. You meet the 55% MBBS eligibility mark (PMDC)."; }
        else if (mPct >= 50) { elig.classList.add("ok"); elig.innerHTML = "✔ MDCAT " + mPct.toFixed(1) + "%. Eligible for BDS (50%), but below the MBBS 55% requirement."; }
        else { elig.classList.add("warn"); elig.innerHTML = "✖ MDCAT " + mPct.toFixed(1) + "%. That is below the 50% minimum. You can improve, InshaAllah. Check our MDCAT prep plan below."; }
      }
      if (invalid) { elig.classList.add("warn"); elig.innerHTML = "⚠ Please check the " + invalid + " marks. Obtained marks should not be more than total marks."; }
      if (anyInput && !invalid && !calcUsed) { calcUsed = true; ssTrack("calculator_use", { calculator: "mdcat" }); }
    }
    ["input", "change"].forEach(ev => calc.addEventListener(ev, e => { if (e.target.matches("input")) compute(); }));
    compute();
  }

  /* ---------------- Resource filters ---------------- */
  $$(".filter-bar").forEach(bar => {
    const scope = document.querySelector(bar.dataset.scope || "body");
    bar.addEventListener("click", e => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      const group = chip.dataset.group;
      $$('.chip[data-group="' + group + '"]', bar).forEach(c => c.classList.toggle("active", c === chip));
      applyFilters(bar, scope);
    });
    function applyFilters() {
      const active = {};
      $$(".chip.active", bar).forEach(c => active[c.dataset.group] = c.dataset.filter);
      $$("[data-filter-item]", scope).forEach(item => {
        const show = Object.keys(active).every(g => active[g] === "all" || (item.dataset[g] || "") === active[g]);
        item.style.display = show ? "" : "none";
      });
      const any = $$("[data-filter-item]", scope).some(i => i.style.display !== "none");
      const empty = $(".filter-empty", scope);
      if (empty) empty.style.display = any ? "none" : "";
    }
  });

  /* ---------------- Share & copy ---------------- */
  $$("[data-share]").forEach(btn => btn.addEventListener("click", () => {
    const url = encodeURIComponent(location.href);
    const text = encodeURIComponent(document.title + " | StudySapiens");
    const net = btn.dataset.share;
    const map = {
      whatsapp: "https://wa.me/?text=" + text + "%20" + url,
      facebook: "https://www.facebook.com/sharer/sharer.php?u=" + url,
      x: "https://twitter.com/intent/tweet?text=" + text + "&url=" + url
    };
    if (net === "copy") {
      navigator.clipboard && navigator.clipboard.writeText(location.href).then(() => toast("Link copied! Share it with your friends 📚"));
    } else if (map[net]) window.open(map[net], "_blank", "noopener,width=640,height=560");
  }));
  $$("[data-copy]").forEach(btn => btn.addEventListener("click", () => {
    navigator.clipboard && navigator.clipboard.writeText(btn.dataset.copy).then(() => toast("Copied: " + btn.dataset.copy));
  }));
  $$("[data-print]").forEach(btn => btn.addEventListener("click", () => window.print()));

  /* ---------------- Toast ---------------- */
  let toastEl = null, toastT = null;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = msg;
    requestAnimationFrame(() => toastEl.classList.add("show"));
    clearTimeout(toastT);
    toastT = setTimeout(() => toastEl.classList.remove("show"), 2600);
  }

  /* ---------------- Forms: newsletter & contact (server-side, mailto fallback) -------------
     Every form keeps data-mailto as the zero-config fallback (opens the email app).
     With values in window.SS_CONFIG (assets/js/ss-config.js) they submit server-side:
       data-ss="newsletter" -> your ESP endpoint (MailerLite / Brevo / Buttondown / Kit…)
       data-ss="contact"    -> Web3Forms (https://api.web3forms.com/submit)
     Both paths push GTM events: newsletter_signup / contact_submit. */
  function formNote(form) {
    const inside = $(".form-success", form);
    if (inside) return inside;
    if (form.nextElementSibling && form.nextElementSibling.classList.contains("form-success")) return form.nextElementSibling;
    return null;
  }
  function formDone(form, msg, isErr, toastMsg) {
    const el = formNote(form);
    if (el) {
      el.textContent = msg;
      el.classList.toggle("form-error", !!isErr);
      el.style.display = "block";
    }
    toast(toastMsg || (isErr ? "Could not send — please try again" : "Sent ✔"));
  }
  function setBusy(form, busy) {
    const b = $('button[type="submit"]', form);
    if (b) { b.disabled = busy; b.style.opacity = busy ? ".6" : ""; }
  }
  function nlEvent(form, method) {
    ssTrack("newsletter_signup", {
      method: method,
      location: form.dataset.location || "",
      interest: form.dataset.interest || ""
    });
  }
  function mailtoCompose(form, fd) {
    const to = form.dataset.mailto;
    let subject = form.dataset.subject || "StudySapiens: Website Message";
    let lines = [];
    fd.forEach((v, k) => {
      if (k === "consent" || k === "website") return;
      if (String(v).trim()) lines.push(k.replace(/[_-]/g, " ").replace(/\b\w/g, m => m.toUpperCase()) + ": " + v);
    });
    if (lines.length) {
      const body = encodeURIComponent(lines.join("\n") + "\n\nSent from studysapiens.com");
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + body;
    }
    if (form.dataset.ss === "newsletter") {
      nlEvent(form, "mailto");
      formDone(form, "Opening your email app. Press Send to subscribe ✔", false, "Opening your email app… just press Send ✉️");
    } else {
      ssTrack("contact_submit", { method: "mailto" });
      formDone(form, "Your email app opened. Press Send there and we'll reply, InshaAllah ✔", false, "Opening your email app… just press Send ✉️");
    }
  }
  function newsletterDone(form) {
    nlEvent(form, "esp");
    formDone(form, "Almost done ✔ Check your inbox (and spam folder) for a confirmation email — click it to finish subscribing.");
  }
  function sendNewsletter(form, fd, CFG) {
    setBusy(form, true);
    const params = new URLSearchParams();
    params.set(CFG.newsletterEmailField || "email", String(fd.get("email") || "").trim());
    Object.keys(CFG.newsletterFields || {}).forEach(k => params.set(k, CFG.newsletterFields[k]));
    if (form.dataset.interest) params.set("interest", form.dataset.interest);
    const body = params.toString();
    const post = noCors => fetch(CFG.newsletterEndpoint, {
      method: "POST",
      mode: noCors ? "no-cors" : undefined,
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body
    });
    post(false).then(r => { if (!r.ok) throw new Error("HTTP " + r.status); })
      .then(() => { setBusy(form, false); newsletterDone(form); })
      .catch(() => {
        // The ESP may not allow reading its response cross-origin; the POST usually
        // still arrived. Retry fire-and-forget, then let the double opt-in email
        // (which the student must click) be the real proof of subscription.
        post(true).then(() => { setBusy(form, false); newsletterDone(form); })
          .catch(() => { setBusy(form, false); mailtoCompose(form, fd); });
      });
  }
  function sendContact(form, fd, CFG) {
    setBusy(form, true);
    const payload = {
      access_key: CFG.contactAccessKey,
      subject: "StudySapiens website: " + (fd.get("topic") || "Contact form"),
      from_name: "StudySapiens Contact Form",
      name: String(fd.get("name") || ""),
      email: String(fd.get("reply_email") || fd.get("email") || ""),
      message: (fd.get("class") ? "[Class: " + fd.get("class") + "]\n" : "") + String(fd.get("message") || ""),
      botcheck: ""
    };
    fetch(CFG.contactEndpoint || "https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(r => r.json().catch(() => ({})))
      .then(res => {
        setBusy(form, false);
        if (res && res.success === false) throw new Error(res.message || "rejected");
        ssTrack("contact_submit", { method: "web3forms" });
        formDone(form, "Message sent ✔ We reply within 1–2 working days. If our reply is not in your inbox, check your spam folder.");
      })
      .catch(() => {
        setBusy(form, false);
        formDone(form, "Could not send right now. Please email us directly at " + (form.dataset.mailto || "admin@studysapiens.com") + " — we reply to every message.", true);
      });
  }
  $$("form[data-mailto]").forEach(form => form.addEventListener("submit", e => {
    e.preventDefault();
    const fd = new FormData(form);
    // Honeypot: humans never see this hidden field. Bots that fill it are
    // dropped silently (they see a fake success message, no data is sent).
    if (String(fd.get("website") || "").trim()) { formDone(form, "Thanks! We got it ✔"); return; }
    const CFG = window.SS_CONFIG || {};
    if (form.dataset.ss === "contact" && CFG.contactAccessKey) return sendContact(form, fd, CFG);
    if (form.dataset.ss === "newsletter" && CFG.newsletterEndpoint) return sendNewsletter(form, fd, CFG);
    mailtoCompose(form, fd);
  }));

  /* "Notify me" buttons on coming-soon cards -> focus the nearest subscribe form
     and remember WHAT the student asked to be notified about (interest). */
  $$("[data-notify]").forEach(btn => btn.addEventListener("click", () => {
    const target = $('form[data-ss="newsletter"]') || $("form[data-mailto]");
    if (!target) return;
    if (btn.dataset.notify) target.dataset.interest = btn.dataset.notify;
    target.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
    const input = $('input[type="email"]', target);
    if (input) setTimeout(() => { try { input.focus({ preventScroll: true }); } catch (err) { input.focus(); } }, 400);
    toast("Leave your email — we'll message you the day it goes live ✉️");
  }));

  /* ---------------- Cookie consent banner (Google Consent Mode v2) ----------------
     First-party banner. Defaults (denied) are set in <head> before GTM loads;
     this banner records the choice and pushes the consent 'update'.
     When you adopt a Google-certified CMP (e.g. AdSense "Privacy & messaging"),
     set SS_CONFIG.consentBanner = false and the certified CMP takes over. */
  (function () {
    const KEY = "ss-consent-v1";
    const CFG = window.SS_CONFIG || {};
    if (CFG.consentBanner === false) return;
    function read() { try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; } }
    function save(analytics, ads) {
      try { localStorage.setItem(KEY, JSON.stringify({ v: 1, analytics: !!analytics, ads: !!ads, ts: new Date().toISOString() })); } catch (e) {}
      const args = {
        ad_storage: ads ? "granted" : "denied",
        ad_user_data: ads ? "granted" : "denied",
        ad_personalization: ads ? "granted" : "denied",
        analytics_storage: analytics ? "granted" : "denied"
      };
      if (window.gtag) window.gtag("consent", "update", args);
      ssTrack("consent_choice", { analytics: !!analytics, ads: !!ads });
    }
    const bar = document.createElement("div");
    bar.className = "cookie-bar no-print";
    bar.id = "cookieBar";
    bar.setAttribute("role", "dialog");
    bar.setAttribute("aria-label", "Cookie settings");
    bar.innerHTML =
      '<div class="cb-txt"><b>Cookies, in one line 🍪</b> ' +
      'We use Google Analytics to count visits anonymously, and (later) ads that keep every note free. ' +
      'We never sell your data. <a href="' + ROOT + 'privacy-policy/">Privacy</a></div>' +
      '<div class="cb-btns">' +
      '<button type="button" class="btn btn-primary btn-sm" data-cb="all">Accept all</button>' +
      '<button type="button" class="btn btn-light-outline btn-sm" data-cb="necessary">Necessary only</button>' +
      '<button type="button" class="btn btn-ghost btn-sm" data-cb="custom">Customize</button>' +
      '</div>' +
      '<div class="cb-opts" hidden>' +
      '<label><input type="checkbox" data-cb-opt="analytics"> Anonymous statistics (Google Analytics)</label>' +
      '<label><input type="checkbox" data-cb-opt="ads"> Advertising (non-personalized unless you allow more)</label>' +
      '<button type="button" class="btn btn-primary btn-sm" data-cb="save">Save my choice</button>' +
      '</div>';
    function openBar(withOpts) {
      const saved = read();
      const opts = $(".cb-opts", bar);
      if (withOpts) {
        const a = $('input[data-cb-opt="analytics"]', bar), d = $('input[data-cb-opt="ads"]', bar);
        a.checked = !!(saved && saved.analytics); d.checked = !!(saved && saved.ads);
        opts.hidden = false;
      }
      if (!bar.parentNode) document.body.appendChild(bar);
      requestAnimationFrame(() => bar.classList.add("show"));
    }
    function closeBar() { bar.classList.remove("show"); }
    bar.addEventListener("click", e => {
      const b = e.target.closest("[data-cb]");
      if (!b) return;
      const act = b.dataset.cb;
      if (act === "all") { save(true, true); closeBar(); toast("Thanks! You can change this anytime in the footer 🍪"); }
      else if (act === "necessary") { save(false, false); closeBar(); toast("Saved — only necessary storage used"); }
      else if (act === "custom") { $(".cb-opts", bar).hidden = false; }
      else if (act === "save") {
        save($('input[data-cb-opt="analytics"]', bar).checked, $('input[data-cb-opt="ads"]', bar).checked);
        closeBar(); toast("Saved — you can change this anytime in the footer");
      }
    });
    // First visit (no choice stored yet): show the banner.
    if (!read()) setTimeout(openBar, 900);
    // Footer "Cookie settings": always available to change the choice.
    $$("[data-cookie-settings]").forEach(btn => btn.addEventListener("click", () => openBar(true)));
  })();

  /* ---------------- PDF download tracking (GTM) ---------------- */
  document.addEventListener("click", e => {
    const a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    const href = a.getAttribute("href") || "";
    if (!/\.pdf(\?|#|$)/i.test(href)) return;
    const name = decodeURIComponent(href.split("/").pop().split(/[?#]/)[0]);
    ssTrack("pdf_download", { file_name: name, link_url: a.href });
  });

  /* ---------------- Active nav ---------------- */
  const pageKey = document.body.dataset.page || "";
  $$(".main-nav a[href]").forEach(a => {
    if (a.dataset.nav === pageKey) a.classList.add("active");
  });

  /* ---------------- Saved chapters (bookmarks on this device) ---------------- */
  (function () {
    const KEY = "ss-saved-v1";
    function readList() { try { const v = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(v) ? v : []; } catch (e) { return []; } }
    function has(url) { return readList().some(x => x.u === url); }
    function writeList(list) { try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) {} paintBadge(); }
    function paintBadge() {
      const n = readList().length;
      $$("[data-saved-badge]").forEach(b => { b.hidden = n === 0; b.textContent = n > 99 ? "99+" : n; });
    }

    // Chapter pages: save / unsave button
    $$("[data-save-chap]").forEach(btn => {
      const rec = { u: btn.dataset.url, t: btn.dataset.title, m: btn.dataset.meta };
      const lbl = $("[data-save-lbl]", btn);
      function paint() {
        const on = has(rec.u);
        btn.classList.toggle("saved", on);
        btn.setAttribute("aria-pressed", on ? "true" : "false");
        if (lbl) lbl.textContent = on ? "Saved" : "Save chapter";
      }
      btn.addEventListener("click", () => {
        let list = readList();
        if (has(rec.u)) { list = list.filter(x => x.u !== rec.u); toast("Removed from your shelf"); }
        else {
          list.unshift(Object.assign({ d: Date.now() }, rec)); list = list.slice(0, 200);
          toast("Saved 🔖. Opens offline too");
          if (navigator.serviceWorker && navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({ type: "CACHE_URLS", urls: [ROOT + rec.u] });
          }
        }
        writeList(list); paint();
      });
      paint();
    });

    // Saved page: render the shelf
    const listEl = $("#savedList");
    if (listEl) {
      const empty = $("#savedEmpty"), toolbar = $("#savedToolbar"), cnt = $("#savedCountTxt"), clearBtn = $("#savedClear");
      const bmIc = '<svg class="svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 3.5h11a1 1 0 011 1V21l-6.5-4.2L5.5 21V4.5a1 1 0 011-1z"/></svg>';
      function renderSaved() {
        const list = readList();
        if (!list.length) {
          listEl.innerHTML = "";
          if (empty) empty.style.display = "";
          if (toolbar) toolbar.hidden = true;
          return;
        }
        if (empty) empty.style.display = "none";
        if (toolbar) toolbar.hidden = false;
        if (cnt) cnt.textContent = list.length + (list.length === 1 ? " chapter saved" : " chapters saved");
        listEl.innerHTML = list.map(it =>
          '<div class="saved-item"><span class="saved-ic">' + bmIc + '</span>' +
          '<div class="saved-tx"><a href="' + ROOT + esc(it.u) + '">' + esc(it.t) + '</a>' +
          '<span class="small muted">' + esc(it.m || "") + "</span></div>" +
          '<button class="tool-btn danger" type="button" data-rm="' + esc(it.u) + '" aria-label="Remove">Remove</button></div>'
        ).join("");
        $$("[data-rm]", listEl).forEach(b => b.addEventListener("click", () => {
          writeList(readList().filter(x => x.u !== b.dataset.rm));
          toast("Removed from your shelf"); renderSaved();
        }));
      }
      if (clearBtn) clearBtn.addEventListener("click", () => { writeList([]); toast("Shelf cleared"); renderSaved(); });
      renderSaved();
    }
    window.addEventListener("storage", e => { if (e.key === KEY) { paintBadge(); if (listEl) { const ev = new Event("ss-rerender-saved"); document.dispatchEvent(ev); } } });
    paintBadge();
  })();

  /* ---------------- Exam countdown ---------------- */
  (function () {
    const box = $("#examTimer");
    if (!box || !window.EXAMS) return;
    const title = $("#etTitle"), note = $("#etNote");
    const cD = $("#etD"), cH = $("#etH"), cM = $("#etM"), cS = $("#etS");
    const exams = window.EXAMS;
    const ids = Object.keys(exams);
    let cls = null;
    try { cls = localStorage.getItem("ss-et-class"); } catch (e) {}
    if (!cls || !exams[cls]) {
      const future = ids.filter(k => new Date(exams[k].date + "T23:59:59") > new Date());
      cls = (future.length ? future : ids).slice()
        .sort((a, b) => new Date(exams[a].date) - new Date(exams[b].date))[0];
    }
    const chips = $$("[data-et-class]", box);
    const pad = n => String(n).padStart(2, "0");
    function paintChips() { chips.forEach(ch => ch.classList.toggle("active", ch.dataset.etClass === cls)); }
    function paint() {
      const info = exams[cls];
      const target = new Date(info.date + "T09:00:00");
      if (title) title.textContent = info.label;
      let diff = target - new Date();
      if (diff <= 0) {
        cD.textContent = "0"; cH.textContent = cM.textContent = cS.textContent = "00";
        if (note) note.textContent = "Best of luck! The exam window has started 🎯";
        return;
      }
      const dd = Math.floor(diff / 864e5);
      cD.textContent = dd;
      cH.textContent = pad(Math.floor(diff / 36e5) % 24);
      cM.textContent = pad(Math.floor(diff / 6e4) % 60);
      cS.textContent = pad(Math.floor(diff / 1e3) % 60);
      if (note) note.textContent = "expected " +
        target.toLocaleDateString("en-PK", { day: "numeric", month: "long", year: "numeric" }) +
        ". Official date sheet pending";
    }
    chips.forEach(ch => ch.addEventListener("click", () => {
      cls = ch.dataset.etClass;
      try { localStorage.setItem("ss-et-class", cls); } catch (e) {}
      paintChips(); paint();
    }));
    paintChips(); paint();
    setInterval(paint, 1000);
  })();

  /* ---------------- PWA: offline + install ---------------- */
  (function () {
    if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol) && location.hostname !== "") {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register(ROOT + "sw.js").catch(() => {});
      });
    }
    // proactive offline caching handled via CACHE_URLS message on save
    let wasOffline = false;
    window.addEventListener("offline", () => {
      if (wasOffline) return; wasOffline = true;
      toast("You are offline. Visited and saved pages still open 📴");
    });
    window.addEventListener("online", () => { wasOffline = false; toast("Back online ✅"); });

    // install prompt
    let deferredPrompt = null;
    const IKEY = "ss-install-hide-until";
    function canShow() {
      try { const t = parseInt(localStorage.getItem(IKEY) || "0", 10); return Date.now() > t; } catch (e) { return true; }
    }
    function showInstallBar() {
      if ($(".install-bar")) return;
      const bar = document.createElement("div");
      bar.className = "install-bar no-print";
      bar.innerHTML =
        '<img src="' + ROOT + 'assets/img/mark.png" alt="StudySapiens app" width="34" height="34">' +
        '<div class="ib-tx"><b>Install StudySapiens</b><span>works offline • one-tap access • free</span></div>' +
        '<button class="btn btn-primary btn-sm" id="ibInstall" type="button">Install</button>' +
        '<button class="ib-x" id="ibClose" type="button" aria-label="Not now">✕</button>';
      document.body.appendChild(bar);
      requestAnimationFrame(() => bar.classList.add("show"));
      $("#ibInstall", bar).addEventListener("click", () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(ch => {
          if (ch.outcome === "accepted") toast("Installed 🎉 find it on your home screen");
          bar.remove(); deferredPrompt = null;
        });
      });
      $("#ibClose", bar).addEventListener("click", () => {
        try { localStorage.setItem(IKEY, String(Date.now() + 14 * 864e5)); } catch (e) {}
        bar.remove();
      });
    }
    window.addEventListener("beforeinstallprompt", e => {
      e.preventDefault();
      deferredPrompt = e;
      if (canShow()) showInstallBar();
    });
  })();

  /* ---------------- Reveal stagger (siblings fly in one after another) ---------------- */
  (function () {
    if (reduced) return;
    const seen = new Map();
    $$(".reveal").forEach(el => {
      if (el.hasAttribute("data-delay")) return;
      const p = el.parentElement;
      const n = seen.get(p) || 0;
      seen.set(p, n + 1);
      if (n > 0) el.style.transitionDelay = Math.min(n * 70, 420) + "ms";
    });
  })();
})();

/* ==========================================================================
   ECAT / UET aggregate calculator (17% Matric + 50% HSSC Part-I + 33% ECAT)
   Lives only on the ECAT corner page; same pattern as the MDCAT calculator.
   ========================================================================== */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const calc = $("#ecatCalc");
  if (!calc) return;
  const ids = ["matric", "fsc", "ecat"];
  const names = { matric: "Matric (SSC)", fsc: "HSSC Part-I (First Year)", ecat: "ECAT" };
  const num = id => parseFloat($("#" + id).value) || 0;
  let calcUsed = false;
  function compute() {
    let total = 0, html = "", anyInput = false, invalid = null;
    ids.forEach(k => {
      const w = parseFloat(calc.dataset["w" + k]);
      const ob = $("#" + k + "Obt"), tot = $("#" + k + "Tot");
      const o = num(k + "Obt"), t = num(k + "Tot");
      if (ob.value || tot.value) anyInput = true;
      if (o < 0 || t <= 0 || o > t) invalid = invalid || names[k];
      const share = t > 0 ? (o / t) * w : 0;
      total += share;
      html += "<tr><td>" + names[k] + " <span class='muted small'>(" + w + "%)</span></td><td>" +
        (t > 0 ? share.toFixed(2) + "%" : "-") + "</td></tr>";
    });
    const C = 2 * Math.PI * 84;
    const gCircle = $(".g-val");
    gCircle.style.strokeDasharray = C;
    gCircle.style.strokeDashoffset = C - Math.min(total, 100) / 100 * C;
    $("#gaugeNum").textContent = total ? total.toFixed(2) + "%" : "0%";
    $("#gaugeBreak").innerHTML = html +
      '<tr><td style="color:#fff;font-weight:800">Aggregate</td><td style="color:var(--gold-300);font-weight:800">' + total.toFixed(2) + "%</td></tr>";
    const elig = $("#eligibility");
    const fo = num("fscObt"), ft = num("fscTot");
    elig.className = "eligibility";
    if (anyInput && !invalid && fo > 0 && ft > 0) {
      const fPct = (fo / ft) * 100;
      if (fPct >= 60) { elig.classList.add("ok"); elig.innerHTML = "✔ First Year " + fPct.toFixed(1) + "%. Merit is built on Part-I; eligibility still needs the complete Intermediate: 60% for engineering, 50% for computing."; }
      else if (fPct >= 50) { elig.classList.add("warn"); elig.innerHTML = "⚠ First Year " + fPct.toFixed(1) + "%. Fine for computing programmes (50%), but engineering needs the complete Intermediate at 60%."; }
      else { elig.classList.add("warn"); elig.innerHTML = "✖ First Year " + fPct.toFixed(1) + "%. Below the usual 50% minimum for the complete Intermediate. Improve now: Part-I carries half your aggregate."; }
    }
    if (invalid) { elig.classList.add("warn"); elig.innerHTML = "⚠ Please check the " + invalid + " marks. Obtained marks should not be more than total marks."; }
    if (anyInput && !invalid && !calcUsed) { calcUsed = true; ssTrack("calculator_use", { calculator: "ecat" }); }
  }
  ["input", "change"].forEach(ev => calc.addEventListener(ev, e => { if (e.target.matches("input")) compute(); }));
  compute();
})();
