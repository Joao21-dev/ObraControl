// ObraControl — interações de frontend (modal, máscara de moeda, categoria/unidade)

document.addEventListener("DOMContentLoaded", () => {
  initMaterialForms(document);
});

// ---------------- Categoria -> Unidade ----------------

function initMaterialForms(scope) {
  scope.querySelectorAll(".js-categoria").forEach((sel) => {
    if (sel.dataset.bound) return;
    sel.dataset.bound = "1";
    populateUnidades(sel);
    sel.addEventListener("change", () => populateUnidades(sel));
  });

  scope.querySelectorAll(".oc-currency-input").forEach((input) => {
    if (input.dataset.bound) return;
    input.dataset.bound = "1";
    const hidden = input.closest(".oc-field").querySelector(".js-valor-hidden");
    if (input.value) maskCurrency(input, hidden);
    input.addEventListener("input", () => maskCurrency(input, hidden));
  });
}

function populateUnidades(catSelect) {
  let mapping;
  try {
    mapping = JSON.parse(catSelect.dataset.mapping || "{}");
  } catch (e) {
    mapping = {};
  }
  const form = catSelect.closest("form");
  const unidadeSelect = form.querySelector(".js-unidade");
  const atual = unidadeSelect.value || catSelect.dataset.currentUnidade || "";
  const opcoes = mapping[catSelect.value] || [];

  unidadeSelect.innerHTML = "";

  if (opcoes.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.disabled = true;
    opt.selected = true;
    opt.textContent = "Selecione a categoria";
    unidadeSelect.appendChild(opt);
    return;
  }

  opcoes.forEach((u) => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === atual) opt.selected = true;
    unidadeSelect.appendChild(opt);
  });

  if (!opcoes.includes(atual)) {
    unidadeSelect.selectedIndex = 0;
  }
}

// ---------------- Máscara de moeda (R$ 0,00) ----------------

function maskCurrency(input, hidden) {
  let digits = input.value.replace(/\D/g, "");
  if (!digits) digits = "0";
  digits = digits.replace(/^0+(?=\d)/, "");
  while (digits.length < 3) digits = "0" + digits;

  const cents = digits.slice(-2);
  let intPart = digits.slice(0, -2).replace(/^0+(?=\d)/, "");
  if (intPart === "") intPart = "0";
  intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

  input.value = intPart + "," + cents;
  if (hidden) hidden.value = intPart.replace(/\./g, "") + "." + cents;
}

// ---------------- Modal ----------------

function openModal(url) {
  fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
    .then((r) => r.text())
    .then((html) => {
      const body = document.getElementById("modal-body");
      body.innerHTML = html;
      document.getElementById("modal-overlay").classList.remove("hidden");
      initMaterialForms(body);
    });
}

function closeModal() {
  document.getElementById("modal-overlay").classList.add("hidden");
  document.getElementById("modal-body").innerHTML = "";
}

document.addEventListener("click", (e) => {
  const link = e.target.closest(".js-modal-link");
  if (link) {
    e.preventDefault();
    openModal(link.getAttribute("href"));
    return;
  }

  const modalBody = document.getElementById("modal-body");

  const cancelBtn = e.target.closest(".js-modal-cancel");
  if (cancelBtn && modalBody.contains(cancelBtn)) {
    e.preventDefault();
    closeModal();
    return;
  }

  if (e.target.id === "modal-overlay" || e.target.closest(".js-modal-close")) {
    closeModal();
  }
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

document.addEventListener("submit", (e) => {
  const form = e.target;
  const modalBody = document.getElementById("modal-body");
  if (!modalBody || !modalBody.contains(form)) return;

  e.preventDefault();
  const submitBtn = form.querySelector("button[type=submit], button:not([type])");
  if (submitBtn) submitBtn.disabled = true;

  fetch(form.action, {
    method: "POST",
    body: new FormData(form),
    headers: { "X-Requested-With": "XMLHttpRequest" },
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) {
        closeModal();
        window.location.reload();
      } else {
        const alertBox = modalBody.querySelector(".js-form-alert");
        if (alertBox) {
          alertBox.innerHTML =
            '<div class="oc-alert oc-alert-danger">' + (data.error || "Não foi possível salvar.") + "</div>";
        }
        if (submitBtn) submitBtn.disabled = false;
      }
    })
    .catch(() => {
      if (submitBtn) submitBtn.disabled = false;
    });
});
