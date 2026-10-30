/* ==========================================================================
   GRUPO ENG — script.js (JavaScript puro, sem bibliotecas)
   ========================================================================== */

/* 1. CONFIGURAÇÃO — números em formato DDI + DDD + telefone, só dígitos.
   O número de construção também pode ser usado com data-wa-service="construction". */
const WHATSAPP_NUMBER = "558899639573";
const WHATSAPP_CONSTRUCTION_NUMBER = "5588997112057";

// Marca o <html> para o CSS saber que o JavaScript está ativo (evita esconder conteúdo sem JS)
document.documentElement.classList.add("js");

/** Monta o link do WhatsApp. encodeURIComponent converte espaços e acentos para formato de URL. */
const waLink = (msg, number = WHATSAPP_NUMBER) => `https://wa.me/${number}?text=${encodeURIComponent(msg)}`;
const waNumberFor = (service) => service === "construction" ? WHATSAPP_CONSTRUCTION_NUMBER : WHATSAPP_NUMBER;

/* 2. BOTÕES DE WHATSAPP — todo elemento com data-wa="mensagem" vira um link pronto */
document.querySelectorAll("[data-wa]").forEach((el) => {
  el.href = waLink(el.dataset.wa, waNumberFor(el.dataset.waService));
  el.target = "_blank";
  el.rel = "noopener";
});

/* 3. MENU MOBILE — abre/fecha o painel e atualiza aria-expanded (acessibilidade) */
const toggle = document.querySelector(".menu-toggle");
const menu = document.getElementById("menu");

function setMenu(open) {
  menu.classList.toggle("is-open", open);
  toggle.setAttribute("aria-expanded", String(open));
  toggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
}
toggle.addEventListener("click", () => setMenu(!menu.classList.contains("is-open")));
menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false))); // fecha ao clicar num link
document.addEventListener("keydown", (e) => e.key === "Escape" && setMenu(false));

/* 4. HEADER — escurece um pouco ao rolar a página */
const header = document.querySelector(".site-header");
const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 40);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

/* 5. FOTOS — se o arquivo local (img/...) não existir, usa a foto de exemplo do data-fallback */
document.querySelectorAll("img[data-fallback]").forEach((img) => {
  img.addEventListener("error", () => {
    if (img.dataset.fallback && img.src !== img.dataset.fallback) img.src = img.dataset.fallback;
  });
  // Caso o erro tenha ocorrido antes do script carregar
  if (img.complete && img.naturalWidth === 0) img.src = img.dataset.fallback;
});

/* 6. GALERIA — filtro por categoria */
const chips = document.querySelectorAll(".chip");
const items = document.querySelectorAll(".gallery .g");

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const filter = chip.dataset.filter;
    chips.forEach((c) => {
      const active = c === chip;
      c.classList.toggle("is-active", active);
      c.setAttribute("aria-pressed", String(active));
    });
    items.forEach((item) => item.classList.toggle("is-hidden", filter !== "todas" && item.dataset.cat !== filter));
  });
});

/* 7. GALERIA — ampliar foto (lightbox com <dialog> nativo) */
const lightbox = document.getElementById("lightbox");
const lbImg = lightbox.querySelector("img");
const lbText = lightbox.querySelector("p");

items.forEach((item) => {
  item.querySelector(".g__open").addEventListener("click", () => {
    const img = item.querySelector("img");
    lbImg.src = img.currentSrc || img.src;
    lbImg.alt = img.alt;
    lbText.textContent = item.querySelector("figcaption").textContent;
    lightbox.showModal();
  });
});
lightbox.querySelector(".lightbox__close").addEventListener("click", () => lightbox.close());
// Clique fora da imagem (no fundo escuro) também fecha
lightbox.addEventListener("click", (e) => e.target === lightbox && lightbox.close());

/* 8. FORMULÁRIO — sem servidor: monta a mensagem e abre o WhatsApp */
document.getElementById("form-contato").addEventListener("submit", (e) => {
  e.preventDefault();
  const d = Object.fromEntries(new FormData(e.target));
  const service = e.target.querySelector('[name="servico"]');
  const serviceName = service.selectedOptions[0].textContent;
  const msg = `Olá! Meu nome é ${d.nome}. Tenho interesse em: ${serviceName}. Meu telefone: ${d.telefone}.` + (d.mensagem ? ` Detalhes: ${d.mensagem}` : "");
  window.open(waLink(msg, waNumberFor(service.selectedOptions[0].dataset.waService)), "_blank", "noopener");
});

/* 9. ANIMAÇÃO DE ENTRADA — IntersectionObserver avisa quando o elemento aparece na tela */
const reveals = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target); // anima só uma vez
      }
    });
  }, { threshold: 0.12 });
  reveals.forEach((el) => io.observe(el));
} else {
  reveals.forEach((el) => el.classList.add("is-visible")); // navegador antigo: mostra tudo
}

/* 10. RODAPÉ — ano atual automático */
document.getElementById("ano").textContent = new Date().getFullYear();
