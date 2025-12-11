# checkout_service.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
import uuid

# Reuse your catalogs
from models import CATALOG, PLANS, ShippingOption  # CATALOG: phones, PLANS: plans

# -----------------------------
# Data contracts (internal)
# -----------------------------
@dataclass
class CartItem:
    sku: str               # "p-iphone-15" | "plan-basic" | "p-iphone-15|plan-basic"
    kind: str              # "phone" | "plan" | "bundle"
    qty: int = 1

@dataclass
class LineSummary:
    label: str
    amount: float

@dataclass
class Quote:
    currency: str
    items: List[LineSummary]
    shipping: LineSummary
    tax: LineSummary
    monthly_total: float
    grand_total: float

# -----------------------------
# Helpers
# -----------------------------
def _round2(x: float) -> float:
    return float(f"{x:.2f}")

def _price_for_item(sku: str, kind: str) -> Tuple[str, float, float]:
    """
    Returns (label, upfront_price, monthly_price) for ONE unit.
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
            raise KeyError(f"Invalid bundle sku '{sku}', expected 'phoneSku|planSku'")
        phone_name, up, _ = _price_for_item(phone_sku, "phone")
        plan_name, _, mo = _price_for_item(plan_sku, "plan")
        return f"{phone_name} + {plan_name}", up, mo

    raise KeyError(f"Unknown kind: {kind}")

# -----------------------------
# Checkout Service
# -----------------------------
class CheckoutService:
    """
    Stateless calculator for quotes & order confirmation.
    Inject tax and shipping policy if you like; sensible defaults provided.
    """

    def __init__(
        self,
        shipping_options: List[ShippingOption],
        currency: str = "EUR",
        tax_rate: float = 0.08,     # 8% example
        tax_on_shipping: bool = True,
    ) -> None:
        self.shipping_options = shipping_options
        self.currency = currency
        self.tax_rate = tax_rate
        self.tax_on_shipping = tax_on_shipping

    # public API --------------------------------------------------------------

    def quote(self, items: List[CartItem], shipping_option_index: int) -> Quote:
        if not items:
            raise ValueError("Cart is empty")
        if not (0 <= shipping_option_index < len(self.shipping_options)):
            raise ValueError("Invalid shipping option")

        # materialize line items
        upfront = 0.0
        monthly = 0.0
        line_summaries: List[LineSummary] = []

        for it in items:
            if it.qty < 1:
                raise ValueError("Quantity must be >= 1")
            label, up, mo = _price_for_item(it.sku, it.kind)
            up_total = up * it.qty
            mo_total = mo * it.qty
            upfront += up_total
            monthly += mo_total
            line_summaries.append(LineSummary(label=f"{label} ×{it.qty}", amount=_round2(up_total)))

        # shipping
        ship = self.shipping_options[shipping_option_index]
        shipping_cost = ship.calculate_cost()

        # tax (on upfront + optionally shipping)
        taxable = upfront + (shipping_cost if self.tax_on_shipping else 0.0)
        tax = taxable * self.tax_rate

        grand = upfront + shipping_cost + tax

        return Quote(
            currency=self.currency,
            items=line_summaries,
            shipping=LineSummary(label=ship.name, amount=_round2(shipping_cost)),
            tax=LineSummary(label=f"Tax ({int(self.tax_rate*100)}%)", amount=_round2(tax)),
            monthly_total=_round2(monthly),
            grand_total=_round2(grand),
        )

    def confirm(self, quote_request: Dict) -> Dict:
        """
        quote_request: {
          "items": [{"sku": "...", "kind": "phone|plan|bundle", "qty": 1}, ...],
          "shipping_option_index": 0
        }
        """
        # compute a fresh quote to avoid tampering
        items = [CartItem(**i) for i in quote_request["items"]]
        q = self.quote(items, quote_request["shipping_option_index"])
        order_id = uuid.uuid4().hex[:12]
        # This is where you'd create a PaymentIntent (Stripe) or save to DB.
        return {
            "order_id": order_id,
            "status": "created",
            "currency": q.currency,
            "grand_total": q.grand_total,
            "monthly_total": q.monthly_total,
        }
