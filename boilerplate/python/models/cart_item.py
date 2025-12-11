from typing import Literal

Kind = Literal["phone", "plan", "bundle"]

@dataclass
class CartItem:
    sku: str
    kind: Kind
    qty: int = 1

    def prices(self, catalog: dict, plans: dict) -> tuple[float, float]:
        if self.qty < 1:
            raise ValueError("qty must be >= 1")

        if self.kind == "phone":
            price = float(catalog[self.sku]["price"])
            return price * self.qty, 0.0

        if self.kind == "plan":
            monthly = float(plans[self.sku]["monthly"])
            return 0.0, monthly * self.qty

        if self.kind == "bundle":
            phone_sku, plan_sku = self.sku.split("|", 1)
            up, _ = CartItem(phone_sku, "phone", self.qty).prices(catalog, plans)
            _, mo = CartItem(plan_sku, "plan", self.qty).prices(catalog, plans)
            return up, mo

        raise ValueError("Unknown kind")

