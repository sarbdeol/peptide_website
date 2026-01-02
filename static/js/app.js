(function () {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // -----------------------
  // Sticky header shadow
  // -----------------------
  const header = $("#siteHeader");
  const onScroll = () => {
    if (!header) return;
    if (window.scrollY > 8) header.style.boxShadow = "0 12px 40px rgba(0,0,0,.25)";
    else header.style.boxShadow = "none";
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // -----------------------
  // Mobile nav toggle
  // -----------------------
  const burger = $("#burgerBtn");
  const mobileNav = $("#mobileNav");
  if (burger && mobileNav) {
    burger.addEventListener("click", () => {
      const expanded = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!expanded));
      mobileNav.hidden = expanded;
    });
  }

  // -----------------------
  // Modal helpers
  // -----------------------
  const openModal = (id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = false;
    document.body.style.overflow = "hidden";
  };
  const closeModal = (el) => {
    if (!el) return;
    el.hidden = true;
    document.body.style.overflow = "";
  };

  $$("[data-open-modal]").forEach((btn) => {
    btn.addEventListener("click", () => openModal(btn.getAttribute("data-open-modal")));
  });
  $$("[data-close-modal]").forEach((btn) => {
    btn.addEventListener("click", () => closeModal(btn.closest(".modal")));
  });

  // -----------------------
  // Drawer (Cart)
  // -----------------------
  const cartDrawer = $("#cartDrawer");
  const openDrawer = () => {
    if (!cartDrawer) return;
    cartDrawer.hidden = false;
    document.body.style.overflow = "hidden";
    renderCart();
  };
  const closeDrawer = () => {
    if (!cartDrawer) return;
    cartDrawer.hidden = true;
    document.body.style.overflow = "";
  };

  const cartBtn = $("#cartBtn");
  const mobileCartBtn = $("#mobileCartBtn");
  if (cartBtn) cartBtn.addEventListener("click", openDrawer);
  if (mobileCartBtn) mobileCartBtn.addEventListener("click", openDrawer);
  $$("[data-close-drawer]").forEach((el) => el.addEventListener("click", closeDrawer));

  // -----------------------
  // Cart storage
  // -----------------------
  const CART_KEY = "labtrust_cart_v1";
  const getCart = () => {
    try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); } catch { return []; }
  };
  const setCart = (items) => localStorage.setItem(CART_KEY, JSON.stringify(items));

  const addToCart = (item) => {
    const cart = getCart();
    const idx = cart.findIndex((x) => x.sku === item.sku);
    if (idx >= 0) cart[idx].qty += item.qty;
    else cart.push(item);
    setCart(cart);
    updateCartBadges();
  };

  const inc = (sku) => {
    const cart = getCart();
    const i = cart.findIndex((x) => x.sku === sku);
    if (i >= 0) cart[i].qty += 1;
    setCart(cart);
    renderCart();
  };

  const dec = (sku) => {
    const cart = getCart();
    const i = cart.findIndex((x) => x.sku === sku);
    if (i >= 0) {
      cart[i].qty -= 1;
      if (cart[i].qty <= 0) cart.splice(i, 1);
    }
    setCart(cart);
    renderCart();
  };

  const subtotal = (cart) => cart.reduce((s, x) => s + Number(x.price) * Number(x.qty), 0);

  const money = (n) => {
    const v = Number(n || 0);
    return "$" + v.toFixed(2);
  };

  const updateCartBadges = () => {
    const cart = getCart();
    const count = cart.reduce((s, x) => s + Number(x.qty), 0);
    const el = $("#cartCount");
    const el2 = $("#cartCountMobile");
    if (el) el.textContent = String(count);
    if (el2) el2.textContent = String(count);
  };

  // Render cart in drawer
  const renderCart = () => {
    updateCartBadges();
    const items = getCart();
    const itemsWrap = $("#cartItems");
    const empty = $("#cartEmpty");
    const sub = $("#cartSubtotal");
    const subLabel = $("#cartSub");
    if (!itemsWrap || !sub || !subLabel) return;

    if (items.length === 0) {
      if (empty) empty.style.display = "block";
      // remove any existing items
      $$(".cartItem", itemsWrap).forEach((x) => x.remove());
      sub.textContent = money(0);
      subLabel.textContent = "0 items";
      return;
    }

    if (empty) empty.style.display = "none";
    $$(".cartItem", itemsWrap).forEach((x) => x.remove());

    items.forEach((it) => {
      const row = document.createElement("div");
      row.className = "cartItem";
      row.innerHTML = `
        <div class="cartItem__thumb">🧪</div>
        <div>
          <div class="cartItem__name">${escapeHtml(it.name)}</div>
          <div class="cartItem__meta">${money(it.price)} • SKU: ${escapeHtml(it.sku)}</div>
        </div>
        <div class="cartItem__actions">
          <button class="smallBtn" type="button" data-dec="${escapeAttr(it.sku)}">-</button>
          <span class="qtyPill">${Number(it.qty)}</span>
          <button class="smallBtn" type="button" data-inc="${escapeAttr(it.sku)}">+</button>
        </div>
      `;
      itemsWrap.appendChild(row);
    });

    // bind
    $$("[data-inc]").forEach((b) => b.addEventListener("click", () => inc(b.getAttribute("data-inc"))));
    $$("[data-dec]").forEach((b) => b.addEventListener("click", () => dec(b.getAttribute("data-dec"))));

    sub.textContent = money(subtotal(items));
    subLabel.textContent = `${items.reduce((s, x) => s + Number(x.qty), 0)} items`;
  };

  // Add-to-cart buttons
  $$("[data-add-to-cart]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const sku = btn.getAttribute("data-sku") || "";
      const name = btn.getAttribute("data-name") || "Item";
      const price = Number(btn.getAttribute("data-price") || 0);
      addToCart({ sku, name, price, qty: 1 });
      // open drawer for feedback
      openDrawer();
    });
  });

  // Product quantity controls
  const qtyInput = $(".qty__input");
  const minusBtn = $("[data-qty-minus]");
  const plusBtn = $("[data-qty-plus]");
  if (qtyInput && minusBtn && plusBtn) {
    const clamp = (n) => Math.max(1, Math.min(99, n));
    minusBtn.addEventListener("click", () => qtyInput.value = String(clamp(Number(qtyInput.value || 1) - 1)));
    plusBtn.addEventListener("click", () => qtyInput.value = String(clamp(Number(qtyInput.value || 1) + 1)));
  }

  // Segmented buttons (size selector demo)
  $$("[data-seg]").forEach((seg) => {
    $$(".seg__btn", seg).forEach((b) => {
      b.addEventListener("click", () => {
        $$(".seg__btn", seg).forEach((x) => x.classList.remove("is-active"));
        b.classList.add("is-active");
      });
    });
  });

  // Tabs (product page)
  const tabs = $$(".tab");
  if (tabs.length) {
    tabs.forEach((t) => {
      t.addEventListener("click", () => {
        const key = t.getAttribute("data-tab");
        tabs.forEach((x) => x.classList.remove("is-active"));
        t.classList.add("is-active");
        $$("[data-tab-pane]").forEach((p) => p.classList.remove("is-active"));
        const pane = document.querySelector(`[data-tab-pane="${key}"]`);
        if (pane) pane.classList.add("is-active");
      });
    });
  }

  // Checkout summary render
  const checkoutItems = $("#checkoutItems");
  const checkoutSubtotal = $("#checkoutSubtotal");
  const checkoutTotal = $("#checkoutTotal");
  const shipping = 9.0;

  const renderCheckout = () => {
    if (!checkoutItems || !checkoutSubtotal || !checkoutTotal) return;
    const items = getCart();
    checkoutItems.innerHTML = "";
    if (!items.length) {
      checkoutItems.innerHTML = `<div class="muted">Your cart is empty. Go back and add a product.</div>`;
      checkoutSubtotal.textContent = money(0);
      checkoutTotal.textContent = money(0);
      return;
    }
    items.forEach((it) => {
      const el = document.createElement("div");
      el.className = "summaryItem";
      el.innerHTML = `
        <span>${escapeHtml(it.name)} <span class="muted">× ${Number(it.qty)}</span></span>
        <strong>${money(Number(it.price) * Number(it.qty))}</strong>
      `;
      checkoutItems.appendChild(el);
    });
    const sub = subtotal(items);
    checkoutSubtotal.textContent = money(sub);
    checkoutTotal.textContent = money(sub + shipping);
  };
  renderCheckout();

  const placeOrderBtn = $("#placeOrderBtn");
  if (placeOrderBtn) {
    placeOrderBtn.addEventListener("click", () => {
      alert("Demo: order placed UI only. Wire to Django Payment + Order API next.");
    });
  }

  // Reveal-on-scroll animations
  const revealEls = $$(".reveal");
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        const delay = e.target.getAttribute("data-delay");
        if (delay) e.target.style.transitionDelay = `${Number(delay)}ms`;
        e.target.classList.add("is-in");
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });

  revealEls.forEach((el) => io.observe(el));

  // On load
  updateCartBadges();

  function escapeHtml(s){
    return String(s)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll('"',"&quot;")
      .replaceAll("'","&#039;");
  }
  function escapeAttr(s){
    // safe for attribute injection
    return escapeHtml(s).replaceAll("`","&#096;");
  }
})();


