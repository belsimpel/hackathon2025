# product_service.py
from __future__ import annotations
from typing import Dict, List, Optional, Literal, Any, Tuple
from enum import Enum
from threading import RLock

# Reuse the product models you already have (from product_controller.py)
# Kind, PhoneProduct, PlanProduct, Product, ProductList
from product_controller import Kind, PhoneProduct, PlanProduct, Product

Sortable = Literal[
    "name", "-name",
    "upfront_price", "-upfront_price",   # phones
    "monthly_fee", "-monthly_fee",       # plans
]

def _sort_key(prod: Product, key: str):
    if key in ("name", "-name"):
        return prod.name.lower()
    if key in ("upfront_price", "-upfront_price"):
        return getattr(prod, "upfront_price", float("inf"))
    if key in ("monthly_fee", "-monthly_fee"):
        return getattr(prod, "monthly_fee", float("inf"))
    return prod.name.lower()

def _matches(
    prod: Product,
    q: Optional[str],
    kind: Optional[Kind],
    brand: Optional[str],
    network: Optional[str],
    min_upfront: Optional[float],
    max_upfront: Optional[float],
) -> bool:
    if not prod.active:
        return False
    if kind and prod.kind != kind:
        return False
    if isinstance(prod, PhoneProduct):
        if brand and prod.brand.lower() != brand.lower():
            return False
        if min_upfront is not None and prod.upfront_price < min_upfront:
            return False
        if max_upfront is not None and prod.upfront_price > max_upfront:
            return False
    if isinstance(prod, PlanProduct):
        if network and prod.network and prod.network.lower() != network.lower():
            return False
    if q:
        needle = q.lower()
        hay = " ".join([
            prod.name or "",
            getattr(prod, "brand", "") or "",
            getattr(prod, "network", "") or "",
            prod.description or "",
            " ".join(getattr(prod, "highlights", []) or []),
        ]).lower()
        if needle not in hay:
            return False
    return True


class ProductService:
    """
    Thread-safe, in-memory product catalog with CRUD + search.
    Swap the dict for a DB later while keeping the same interface.
    """

    def __init__(self, seed: Optional[List[Product]] = None) -> None:
        self._lock = RLock()
        self._catalog: Dict[str, Product] = {}
        if seed:
            with self._lock:
                for p in seed:
                    self._catalog[p.sku] = p

    # ---------------------------
    # Reads
    # ---------------------------
    def list(
        self,
        *,
        q: Optional[str] = None,
        kind: Optional[Kind] = None,
        brand: Optional[str] = None,
        network: Optional[str] = None,
        min_upfront: Optional[float] = None,
        max_upfront: Optional[float] = None,
        sort: Sortable = "name",
        page: int = 1,
        page_size: int = 12,
    ) -> Tuple[List[Product], int]:
        """Return (items, total) for given filters and pagination."""
        with self._lock:
            items = [
                p for p in self._catalog.values()
                if _matches(p, q, kind, brand, network, min_upfront, max_upfront)
            ]

            reverse = sort.startswith("-") if sort else False
            key = sort[1:] if reverse else (sort or "name")
            items.sort(key=lambda p: _sort_key(p, key if not reverse else f"-{key}"), reverse=reverse)

            total = len(items)
            start = max(0, (page - 1) * page_size)
            end = start + page_size
            return items[start:end], total

    def get(self, sku: str) -> Product:
        with self._lock:
            prod = self._catalog.get(sku)
            if not prod:
                raise KeyError("Product not found")
            return prod

    # ---------------------------
    # Writes
    # ---------------------------
    def create(self, payload: dict) -> Product:
        """Create a product from a dict (Pydantic-validated)."""
        kind = payload.get("kind")
        model = PhoneProduct if kind == Kind.phone else PlanProduct if kind == Kind.plan else None
        if model is None:
            raise ValueError("Invalid kind; must be 'phone' or 'plan'")

        prod = model.model_validate(payload)  # pydantic v2
        with self._lock:
            if prod.sku in self._catalog:
                raise ValueError("SKU already exists")
            self._catalog[prod.sku] = prod
            return prod

    def update(self, sku: str, updates: dict[str, Any]) -> Product:
        """Partial update; revalidates against the proper Pydantic model."""
        with self._lock:
            existing = self._catalog.get(sku)
            if not existing:
                raise KeyError("Product not found")

            data = existing.model_dump()
            data.update(updates or {})

            kind = data.get("kind")
            model = PhoneProduct if kind == Kind.phone else PlanProduct if kind == Kind.plan else None
            if model is None:
                raise ValueError("Invalid kind")

            updated = model.model_validate(data)
            self._catalog[sku] = updated
            return updated

    def upsert_many(self, items: List[dict]) -> int:
        """Bulk create/update. Returns count upserted."""
        count = 0
        with self._lock:
            for it in items:
                kind = it.get("kind")
                model = PhoneProduct if kind == Kind.phone else PlanProduct if kind == Kind.plan else None
                if model is None:
                    continue
                prod = model.model_validate(it)
                self._catalog[prod.sku] = prod
                count += 1
        return count

    def delete(self, sku: str) -> None:
        with self._lock:
            if sku not in self._catalog:
                raise KeyError("Product not found")
            del self._catalog[sku]

    # ---------------------------
    # Utilities
    # ---------------------------
    def count(self) -> int:
        with self._lock:
            return len(self._catalog)

    def brands(self) -> List[str]:
        with self._lock:
            seen = set()
            for p in self._catalog.values():
                if isinstance(p, PhoneProduct):
                    seen.add(p.brand)
            return sorted(seen)

    def networks(self) -> List[str]:
        with self._lock:
            seen = set()
            for p in self._catalog.values():
                if isinstance(p, PlanProduct) and p.network:
                    seen.add(p.network)
            return sorted(seen)
