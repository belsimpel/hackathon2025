# cart_service.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Tuple, List

# Reuse your catalog dictionaries
from models import CATALOG, PLANS  # {"sku": {"price": ...}} and {"sku": {"monthly": ...}}

# -----------------------------
# Data structures returned by the service
# -----------------------------
@dataclass
class CartLine:
    sku: str
    kind: str          # "phone" | "plan" | "bundle"
    qty: int
    label: str
    upfront_subtotal: float
    monthly_subtotal: float

@dataclass
class CartTotals:
    upfront_total: float
    monthly_total: float
    item_count: int

@dataclass
class CartView:
    items: List[CartLine]
    totals: CartTotals

# -----------------------------
# Pricing helpers (shared logic)
# -----------------------------
def _price_for_item(sku: str, kind: str) -> tuple[str, float, float]:
    """
    Returns (label, upfront_price, monthly_price) for ONE unit of the item.
    """
    if kind == "phone":
        prod = CATALOG.get(sku)
        if not prod:
            raise KeyError(f"Unknown phone SKU: {sku}")
        return prod["name"], float(prod["price"]), 0.0

    if kind == "plan":
        plan = PLANS.get(sku)
        if not plan:
            raise KeyError(f"Unknown plan SKU: {sku}")
        return plan["name"], 0.0, float(plan["monthly"])

    if kind == "bundle":
        try:
            phone_sku, plan_sku = sku.split("|", 1)
        except ValueError:
            raise KeyError(f"Invalid bundle SKU format (expected 'phone|plan'): {sku}")
        phone_name, up, _ = _price_for_item(phone_sku, "phone")
        plan_name, _, mo = _price_for_item(plan_sku, "plan")
        return f"{phone_name} + {plan_name}", up, mo

    raise KeyError(f"Unknown kind: {kind}")

# -----------------------------
# Storage interface (you can swap this for Redis/DB later)
# -----------------------------
class InMemoryCartStore:
    """
    carts[session_id] = dict[ (sku, kind) -> qty ]
    """
    def __init__(self) -> None:
        self.carts: Dict[str, Dict[Tuple[str, str], int]] = {}

    def get_cart(self, session_id: str) -> Dict[Tuple[str, str], int]:
        return self.carts.setdefault(session_id, {})

    def set_qty(self, session_id: str, sku: str, kind: str, qty: int) -> None:
        cart = self.get_cart(session_id)
        key = (sku, kind)
        if qty <= 0:
            cart.pop(key, None)
        else:
            cart[key] = qty

    def clear(self, session_id: str) -> None:
        self.carts[session_id] = {}

# -----------------------------
# Cart Service
# -----------------------------
class CartService:
    """
    Business logic for cart management. Stateless; uses a store object for persistence.
    """
    def __init__(self, store: InMemoryCartStore | None = None) -> None:
        self.store = store or InMemoryCartStore()

    # ----- public API -----
    def view(self, session_id: str) -> CartView:
        cart_map = self.store.get_cart(session_id)
        return self._materialize(cart_map)

    def add(self, session_id: str, sku: str, kind: str, qty: int = 1) -> CartView:
        if qty < 1:
            raise ValueError("qty must be >= 1")
        # validate by pricing once
        _price_for_item(sku, kind)
        cart = self.store.get_cart(session_id)
        key = (sku, kind)
        cart[key] = cart.get(key, 0) + qty
        return self._materialize(cart)

    def update_qty(self, session_id: str, sku: str, kind: str, qty: int) -> CartView:
        if qty < 0:
            raise ValueError("qty must be >= 0")
        if qty > 0:
            # validate only if setting positive qty
            _price_for_item(sku, kind)
        self.store.set_qty(session_id, sku, kind, qty)
        return self.view(session_id)

    def remove(self, session_id: str, sku: str, kind: str) -> CartView:
        self.store.set_qty(session_id, sku, kind, 0)
        return self.view(session_id)

    def clear(self, session_id: str) -> CartView:
        self.store.clear(session_id)
        return self.view(session_id)

    # ----- internal -----
    def _materialize(self, cart_map: Dict[Tuple[str, str], int]) -> CartView:
        items: List[CartLine] = []
        upfront_total = 0.0
        monthly_total = 0.0

        for (sku, kind), qty in cart_map.items():
            if qty <= 0:
                continue
            label, up, mo = _price_for_item(sku, kind)
            up_sub = round(up * qty, 2)
            mo_sub = round(mo * qty, 2)
            upfront_total += up_sub
            monthly_total += mo_sub
            items.append(
                CartLine(
                    sku=sku,
                    kind=kind,
                    qty=qty,
                    label=label,
                    upfront_subtotal=up_sub,
                    monthly_subtotal=mo_sub,
                )
            )

        totals = CartTotals(
            upfront_total=round(upfront_total, 2),
            monthly_total=round(monthly_total, 2),
            item_count=sum(qty for qty in cart_map.values() if qty > 0),
        )
        return CartView(items=items, totals=totals)
