document.addEventListener("DOMContentLoaded", () => {

  // ── Active nav link highlight ──
  const path = location.pathname;
  document.querySelectorAll("nav a").forEach(a => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });

  // ── Form submit spinner ──
  document.querySelectorAll("form").forEach(f => {
    f.addEventListener("submit", () => {
      const b = f.querySelector('button[type="submit"], button:not([type])');
      if (b && f.checkValidity()) {
        b.disabled = true;
        b.textContent = "Saving…";
      }
    });
  });

  // ── Theme toggle ──
  const btn = document.getElementById("themeToggle");
  if (!btn) return;
  const root = document.documentElement;

  const apply = t => {
    root.setAttribute("data-theme", t);
    btn.textContent = t === "dark" ? "☀️" : "🌙";
    btn.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
  };

  // Init from storage, fallback to system preference
  const saved = localStorage.getItem("theme");
  const system = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  apply(saved || system);

  btn.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next);
    apply(next);
  });

});
