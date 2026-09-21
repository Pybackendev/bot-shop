const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Всё крутится на одном Render-сервисе — API и webapp на одном домене,
// поэтому просто берём текущий origin, без отдельного backend-URL
const API_BASE = window.location.origin;

// Корзина в localStorage — переживает закрытие Mini App (в отличие от sessionStorage)
const CART_KEY = "shop_cart_v1";

function loadCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || {};
  } catch {
    return {};
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  renderCartCount(cart);
}

let cart = loadCart();
let productsById = {};

function renderCartCount(cart) {
  const count = Object.values(cart).reduce((s, i) => s + i.quantity, 0);
  document.getElementById("cart-count").textContent = count;
}

async function loadCatalog() {
  const res = await fetch(`${API_BASE}/api/products`);
  const products = await res.json();
  productsById = Object.fromEntries(products.map((p) => [p.id, p]));

  const container = document.getElementById("catalog");
  container.innerHTML = "";
  products.forEach((p) => {
    const card = document.createElement("div");
    card.className = "product-card";
    const imgSrc = p.photo_file_id ? `${API_BASE}/api/products/${p.id}/photo` : "";
    card.innerHTML = `
      <img src="${imgSrc}" alt="" onerror="this.style.visibility='hidden'">
      <div class="info">
        <strong>${p.name}</strong><br/>
        <span>${p.description || ""}</span><br/>
        <b>${p.price} грн</b>
      </div>
      <button data-id="${p.id}">В корзину</button>
    `;
    card.querySelector("button").addEventListener("click", () => addToCart(p.id));
    container.appendChild(card);
  });
}

function addToCart(productId) {
  const item = cart[productId] || { productId, quantity: 0 };
  item.quantity += 1;
  cart[productId] = item;
  saveCart(cart);
  tg.HapticFeedback.impactOccurred("light");
}

function renderCart() {
  const container = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total");
  container.innerHTML = "";

  const entries = Object.values(cart);
  if (entries.length === 0) {
    container.innerHTML = "<p>Корзина пуста</p>";
    totalEl.textContent = "";
    document.getElementById("checkout-form").style.display = "none";
    tg.MainButton.hide();
    return;
  }

  let total = 0;
  entries.forEach((item) => {
    const product = productsById[item.productId];
    if (!product) return;
    const subtotal = product.price * item.quantity;
    total += subtotal;

    const row = document.createElement("div");
    row.className = "cart-row";
    row.innerHTML = `
      <span>${product.name} × ${item.quantity}</span>
      <span>${subtotal} грн</span>
      <button data-id="${item.productId}">✕</button>
    `;
    row.querySelector("button").addEventListener("click", () => {
      delete cart[item.productId];
      saveCart(cart);
      renderCart();
    });
    container.appendChild(row);
  });

  totalEl.textContent = `Итого: ${total} грн`;
  document.getElementById("checkout-form").style.display = "block";

  tg.MainButton.setText("Оформить заказ");
  tg.MainButton.show();
  tg.MainButton.onClick(submitOrder);
}

async function submitOrder() {
  const items = Object.values(cart).map((i) => ({
    product_id: i.productId,
    quantity: i.quantity,
  }));

  const body = {
    full_name: document.getElementById("f-name").value,
    phone: document.getElementById("f-phone").value,
    address: document.getElementById("f-address").value,
    delivery_method: document.getElementById("f-delivery").value,
    payment_method: document.getElementById("f-payment").value,
    items,
  };

  if (!body.full_name || !body.phone) {
    tg.showAlert("Заполни имя и телефон");
    return;
  }

  tg.MainButton.showProgress();
  try {
    const res = await fetch(`${API_BASE}/api/order`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": tg.initData,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Ошибка сервера");
    }

    const order = await res.json();

    cart = {};
    saveCart(cart);

    if (order.payment_url) {
      tg.openLink(order.payment_url);
    } else {
      tg.showAlert(`Заказ #${order.id} оформлен!`);
    }
    tg.close();
  } catch (e) {
    tg.showAlert(`Не получилось оформить заказ: ${e.message}`);
  } finally {
    tg.MainButton.hideProgress();
  }
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".screen").forEach((s) => s.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");

    if (tab.dataset.tab === "cart") {
      renderCart();
    } else {
      tg.MainButton.hide();
    }
  });
});

renderCartCount(cart);
loadCatalog();
