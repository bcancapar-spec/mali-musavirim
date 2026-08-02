#!/usr/bin/env python3
"""Deterministic local calculation engine for the Muhasebecim skill.

All decimal JSON inputs must be strings. Integer counters may be JSON integers.
No tax rate, threshold, exchange rate, or index is embedded in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any, Callable


ENGINE_VERSION = "0.0.3"
getcontext().prec = 34
getcontext().rounding = ROUND_HALF_UP


class InputError(ValueError):
    """Raised when a calculation input is invalid."""


def dec(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise InputError(f"{name} must be a decimal string or integer; float is forbidden")
    if not isinstance(value, (str, int, Decimal)):
        raise InputError(f"{name} must be a decimal string or integer")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InputError(f"{name} is not a valid decimal") from exc
    if not result.is_finite():
        raise InputError(f"{name} must be finite")
    return result


def integer(value: Any, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError(f"{name} must be an integer")
    if value < minimum:
        raise InputError(f"{name} must be at least {minimum}")
    return value


def precision(payload: dict[str, Any]) -> int:
    return integer(payload.get("precision", 2), "precision", 0)


def quantum(places: int) -> Decimal:
    return Decimal(1).scaleb(-places)


def rnd(value: Decimal, places: int) -> Decimal:
    return value.quantize(quantum(places), rounding=ROUND_HALF_UP)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def decimal_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: decimal_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_json(item) for item in value]
    return value


def require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise InputError(f"{key} must be a list")
    return value


def journal_check(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    lines = require_list(payload, "entries")
    if not lines:
        raise InputError("entries must not be empty")
    total_debit = Decimal(0)
    total_credit = Decimal(0)
    normalized = []
    errors: list[str] = []
    for index, line in enumerate(lines, start=1):
        if not isinstance(line, dict):
            raise InputError(f"entries[{index - 1}] must be an object")
        debit = rnd(dec(line.get("debit", "0"), f"entries[{index - 1}].debit"), places)
        credit = rnd(dec(line.get("credit", "0"), f"entries[{index - 1}].credit"), places)
        if debit < 0 or credit < 0:
            errors.append(f"line {index}: debit and credit must be non-negative")
        if debit > 0 and credit > 0:
            errors.append(f"line {index}: one line cannot contain both debit and credit")
        if debit == 0 and credit == 0:
            errors.append(f"line {index}: both debit and credit are zero")
        total_debit += debit
        total_credit += credit
        normalized.append(
            {
                "line": line.get("line", index),
                "account": str(line.get("account", "")),
                "description": str(line.get("description", "")),
                "debit": debit,
                "credit": credit,
            }
        )
    difference = rnd(total_debit - total_credit, places)
    balanced = difference == 0 and not errors
    return {
        "entries": normalized,
        "total_debit": rnd(total_debit, places),
        "total_credit": rnd(total_credit, places),
        "difference": difference,
        "balanced": balanced,
        "errors": errors,
        "invariants": {
            "debits_equal_credits": difference == 0,
            "valid_line_sides": not errors,
        },
    }


def straight_line_depreciation(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    cost = rnd(dec(payload.get("cost"), "cost"), places)
    residual = rnd(dec(payload.get("residual_value", "0"), "residual_value"), places)
    periods = integer(payload.get("life_periods"), "life_periods", 1)
    if cost < 0 or residual < 0 or residual > cost:
        raise InputError("require 0 <= residual_value <= cost")
    depreciable = rnd(cost - residual, places)
    unrounded = depreciable / Decimal(periods)
    schedule = []
    accumulated = Decimal(0)
    opening = cost
    for period in range(1, periods + 1):
        depreciation = rnd(unrounded, places) if period < periods else rnd(depreciable - accumulated, places)
        closing = rnd(opening - depreciation, places)
        accumulated = rnd(accumulated + depreciation, places)
        schedule.append(
            {
                "period": period,
                "opening_carrying_amount": opening,
                "depreciation": depreciation,
                "accumulated_depreciation": accumulated,
                "closing_carrying_amount": closing,
            }
        )
        opening = closing
    return {
        "cost": cost,
        "residual_value": residual,
        "depreciable_amount": depreciable,
        "schedule": schedule,
        "invariants": {
            "depreciation_equals_depreciable_amount": accumulated == depreciable,
            "closing_equals_residual_value": opening == residual,
        },
        "warning": "Useful life and residual value must be sourced under the selected reporting/tax framework.",
    }


def declining_balance_depreciation(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    cost = rnd(dec(payload.get("cost"), "cost"), places)
    residual = rnd(dec(payload.get("residual_value", "0"), "residual_value"), places)
    rate = dec(payload.get("rate"), "rate")
    periods = integer(payload.get("life_periods"), "life_periods", 1)
    close_last = bool(payload.get("close_to_residual_on_last", True))
    if cost < 0 or residual < 0 or residual > cost:
        raise InputError("require 0 <= residual_value <= cost")
    if rate <= 0 or rate > 1:
        raise InputError("rate must be in (0, 1]")
    schedule = []
    opening = cost
    accumulated = Decimal(0)
    for period in range(1, periods + 1):
        maximum = rnd(opening - residual, places)
        calculated = rnd(opening * rate, places)
        depreciation = maximum if period == periods and close_last else min(calculated, maximum)
        depreciation = max(depreciation, Decimal(0))
        closing = rnd(opening - depreciation, places)
        accumulated = rnd(accumulated + depreciation, places)
        schedule.append(
            {
                "period": period,
                "opening_carrying_amount": opening,
                "rate": rate,
                "depreciation": depreciation,
                "accumulated_depreciation": accumulated,
                "closing_carrying_amount": closing,
            }
        )
        opening = closing
    return {
        "schedule": schedule,
        "invariants": {
            "not_below_residual": opening >= residual,
            "closing_equals_residual_when_requested": (not close_last) or opening == residual,
        },
        "warning": "The supplied rate and method eligibility must be verified for the relevant period.",
    }


def present_value(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    rate = dec(payload.get("rate"), "rate")
    if rate <= -1:
        raise InputError("rate must be greater than -1")
    cashflows = require_list(payload, "cashflows")
    if not cashflows:
        raise InputError("cashflows must not be empty")
    rows = []
    total = Decimal(0)
    for index, item in enumerate(cashflows):
        if not isinstance(item, dict):
            raise InputError(f"cashflows[{index}] must be an object")
        period = integer(item.get("period"), f"cashflows[{index}].period", 0)
        amount = dec(item.get("amount"), f"cashflows[{index}].amount")
        factor = (Decimal(1) + rate) ** period
        pv = amount / factor
        total += pv
        rows.append({"period": period, "amount": amount, "discount_factor": Decimal(1) / factor, "present_value": rnd(pv, places)})
    return {
        "rate": rate,
        "cashflows": rows,
        "present_value": rnd(total, places),
        "invariants": {"cashflow_count_matches": len(rows) == len(cashflows)},
        "warning": "Rate periodicity must match cash-flow periods and must be independently sourced or justified.",
    }


def effective_interest(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    opening = rnd(dec(payload.get("initial_carrying_amount"), "initial_carrying_amount"), places)
    rate = dec(payload.get("rate"), "rate")
    payments = require_list(payload, "payments")
    if opening < 0:
        raise InputError("initial_carrying_amount must be non-negative")
    if rate <= -1:
        raise InputError("rate must be greater than -1")
    schedule = []
    for index, raw_payment in enumerate(payments, start=1):
        payment = rnd(dec(raw_payment, f"payments[{index - 1}]"), places)
        interest = rnd(opening * rate, places)
        closing = rnd(opening + interest - payment, places)
        schedule.append(
            {
                "period": index,
                "opening_carrying_amount": opening,
                "effective_interest": interest,
                "payment": payment,
                "closing_carrying_amount": closing,
            }
        )
        opening = closing
    return {
        "rate": rate,
        "schedule": schedule,
        "ending_carrying_amount": opening,
        "invariants": {"period_count_matches": len(schedule) == len(payments)},
    }


def weighted_average_inventory(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    quantity = dec(payload.get("opening_quantity", "0"), "opening_quantity")
    unit_cost = dec(payload.get("opening_unit_cost", "0"), "opening_unit_cost")
    if quantity < 0 or unit_cost < 0:
        raise InputError("opening quantity and unit cost must be non-negative")
    inventory_cost = quantity * unit_cost
    cogs = Decimal(0)
    rows = []
    for index, txn in enumerate(require_list(payload, "transactions")):
        if not isinstance(txn, dict):
            raise InputError(f"transactions[{index}] must be an object")
        kind = txn.get("type")
        qty = dec(txn.get("quantity"), f"transactions[{index}].quantity")
        if qty <= 0:
            raise InputError(f"transactions[{index}].quantity must be positive")
        if kind == "purchase":
            purchase_cost = dec(txn.get("unit_cost"), f"transactions[{index}].unit_cost")
            if purchase_cost < 0:
                raise InputError("purchase unit cost must be non-negative")
            inventory_cost += qty * purchase_cost
            quantity += qty
            average = inventory_cost / quantity
            movement_cost = qty * purchase_cost
        elif kind == "sale":
            if qty > quantity:
                raise InputError(f"transactions[{index}] would create negative inventory")
            average = inventory_cost / quantity if quantity else Decimal(0)
            movement_cost = qty * average
            inventory_cost -= movement_cost
            quantity -= qty
            cogs += movement_cost
            average = inventory_cost / quantity if quantity else Decimal(0)
        else:
            raise InputError(f"transactions[{index}].type must be purchase or sale")
        rows.append(
            {
                "sequence": index + 1,
                "type": kind,
                "quantity": qty,
                "movement_cost": rnd(movement_cost, places),
                "ending_quantity": quantity,
                "moving_average_unit_cost": rnd(average, places),
                "ending_inventory_cost": rnd(inventory_cost, places),
            }
        )
    return {
        "transactions": rows,
        "cost_of_goods_sold": rnd(cogs, places),
        "ending_quantity": quantity,
        "ending_inventory_cost": rnd(inventory_cost, places),
        "ending_unit_cost": rnd(inventory_cost / quantity, places) if quantity else Decimal(0),
        "invariants": {"non_negative_inventory": quantity >= 0 and inventory_cost >= 0},
    }


def fifo_inventory(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    layers: list[list[Decimal]] = []
    opening_layers = payload.get("opening_layers", [])
    if not isinstance(opening_layers, list):
        raise InputError("opening_layers must be a list")
    for index, layer in enumerate(opening_layers):
        if not isinstance(layer, dict):
            raise InputError(f"opening_layers[{index}] must be an object")
        qty = dec(layer.get("quantity"), f"opening_layers[{index}].quantity")
        cost = dec(layer.get("unit_cost"), f"opening_layers[{index}].unit_cost")
        if qty <= 0 or cost < 0:
            raise InputError("opening layer quantity must be positive and cost non-negative")
        layers.append([qty, cost])
    cogs = Decimal(0)
    rows = []
    for index, txn in enumerate(require_list(payload, "transactions")):
        if not isinstance(txn, dict):
            raise InputError(f"transactions[{index}] must be an object")
        kind = txn.get("type")
        qty = dec(txn.get("quantity"), f"transactions[{index}].quantity")
        if qty <= 0:
            raise InputError("transaction quantity must be positive")
        movement_cost = Decimal(0)
        if kind == "purchase":
            cost = dec(txn.get("unit_cost"), f"transactions[{index}].unit_cost")
            if cost < 0:
                raise InputError("purchase unit cost must be non-negative")
            layers.append([qty, cost])
            movement_cost = qty * cost
        elif kind == "sale":
            available = sum((layer[0] for layer in layers), Decimal(0))
            if qty > available:
                raise InputError(f"transactions[{index}] would create negative inventory")
            remaining = qty
            while remaining > 0:
                layer_qty, layer_cost = layers[0]
                used = min(remaining, layer_qty)
                movement_cost += used * layer_cost
                layer_qty -= used
                remaining -= used
                if layer_qty == 0:
                    layers.pop(0)
                else:
                    layers[0][0] = layer_qty
            cogs += movement_cost
        else:
            raise InputError(f"transactions[{index}].type must be purchase or sale")
        rows.append({"sequence": index + 1, "type": kind, "quantity": qty, "movement_cost": rnd(movement_cost, places)})
    ending_cost = sum((qty * cost for qty, cost in layers), Decimal(0))
    ending_qty = sum((qty for qty, _ in layers), Decimal(0))
    return {
        "transactions": rows,
        "ending_layers": [{"quantity": qty, "unit_cost": cost, "layer_cost": rnd(qty * cost, places)} for qty, cost in layers],
        "cost_of_goods_sold": rnd(cogs, places),
        "ending_quantity": ending_qty,
        "ending_inventory_cost": rnd(ending_cost, places),
        "invariants": {"non_negative_inventory": ending_qty >= 0 and ending_cost >= 0},
    }


def fx_valuation(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    amount = dec(payload.get("foreign_amount"), "foreign_amount")
    book_rate = dec(payload.get("book_rate"), "book_rate")
    closing_rate = dec(payload.get("closing_rate"), "closing_rate")
    if book_rate < 0 or closing_rate < 0:
        raise InputError("rates must be non-negative")
    book_value = rnd(amount * book_rate, places)
    closing_value = rnd(amount * closing_rate, places)
    return {
        "foreign_amount": amount,
        "book_rate": book_rate,
        "closing_rate": closing_rate,
        "book_value": book_value,
        "closing_value": closing_value,
        "valuation_difference": rnd(closing_value - book_value, places),
        "warning": "Classify the difference as gain/loss according to the account's asset or liability nature.",
    }


def index_restatement(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    amount = dec(payload.get("amount"), "amount")
    base_index = dec(payload.get("base_index"), "base_index")
    closing_index = dec(payload.get("closing_index"), "closing_index")
    if base_index <= 0 or closing_index <= 0:
        raise InputError("indices must be positive")
    coefficient = closing_index / base_index
    restated = rnd(amount * coefficient, places)
    return {
        "amount": amount,
        "base_index": base_index,
        "closing_index": closing_index,
        "coefficient": coefficient,
        "restated_amount": restated,
        "restatement_difference": rnd(restated - amount, places),
        "warning": "This generic index operation does not determine legal scope, correction dates, or monetary/non-monetary classification.",
    }


def impairment(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    carrying = rnd(dec(payload.get("carrying_amount"), "carrying_amount"), places)
    value_in_use = rnd(dec(payload.get("value_in_use"), "value_in_use"), places)
    fair_less_costs = rnd(dec(payload.get("fair_value_less_disposal_costs"), "fair_value_less_disposal_costs"), places)
    if min(carrying, value_in_use, fair_less_costs) < 0:
        raise InputError("amounts must be non-negative")
    recoverable = max(value_in_use, fair_less_costs)
    loss = max(rnd(carrying - recoverable, places), Decimal(0))
    return {
        "carrying_amount": carrying,
        "recoverable_amount": recoverable,
        "impairment_loss": loss,
        "post_impairment_carrying_amount": rnd(carrying - loss, places),
        "invariants": {"not_below_recoverable_amount": rnd(carrying - loss, places) >= min(carrying, recoverable)},
    }


def deferred_tax(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    carrying = dec(payload.get("carrying_amount"), "carrying_amount")
    tax_base = dec(payload.get("tax_base"), "tax_base")
    rate = dec(payload.get("tax_rate"), "tax_rate")
    position_type = payload.get("position_type")
    if position_type not in {"asset", "liability"}:
        raise InputError("position_type must be asset or liability")
    if rate < 0 or rate > 1:
        raise InputError("tax_rate must be in [0, 1]")
    difference = carrying - tax_base
    taxable_difference = difference if position_type == "asset" else -difference
    classification = "deferred_tax_liability" if taxable_difference > 0 else "deferred_tax_asset" if taxable_difference < 0 else "none"
    tax_effect = rnd(abs(taxable_difference) * rate, places)
    return {
        "position_type": position_type,
        "carrying_amount": carrying,
        "tax_base": tax_base,
        "temporary_difference": difference,
        "classification": classification,
        "tax_rate": rate,
        "tax_effect": tax_effect,
        "warning": "Recognition exceptions, recoverability, enacted-rate timing, and presentation require separate framework analysis.",
    }


def _sum_amounts(items: list[Any], name: str) -> tuple[Decimal, list[dict[str, Any]]]:
    total = Decimal(0)
    rows = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise InputError(f"{name}[{index}] must be an object")
        amount = dec(item.get("amount"), f"{name}[{index}].amount")
        if amount < 0:
            raise InputError(f"{name}[{index}].amount must be non-negative")
        total += amount
        rows.append({"description": str(item.get("description", "")), "amount": amount, "difference_type": item.get("difference_type")})
    return total, rows


def tax_reconciliation(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    profit = dec(payload.get("accounting_profit"), "accounting_profit")
    additions_total, additions = _sum_amounts(require_list(payload, "additions"), "additions")
    deductions_total, deductions = _sum_amounts(require_list(payload, "deductions"), "deductions")
    losses = dec(payload.get("loss_carryforwards_used", "0"), "loss_carryforwards_used")
    rate = dec(payload.get("tax_rate"), "tax_rate")
    credits = dec(payload.get("tax_credits", "0"), "tax_credits")
    if losses < 0 or credits < 0 or rate < 0 or rate > 1:
        raise InputError("losses and credits must be non-negative; tax_rate must be in [0, 1]")
    before_losses = profit + additions_total - deductions_total
    taxable = max(before_losses - losses, Decimal(0))
    gross_tax = rnd(taxable * rate, places)
    net_tax = max(rnd(gross_tax - credits, places), Decimal(0))
    return {
        "accounting_profit": profit,
        "additions": additions,
        "additions_total": rnd(additions_total, places),
        "deductions": deductions,
        "deductions_total": rnd(deductions_total, places),
        "profit_before_loss_relief": rnd(before_losses, places),
        "loss_carryforwards_used": losses,
        "taxable_income": rnd(taxable, places),
        "tax_rate": rate,
        "gross_tax": gross_tax,
        "tax_credits": credits,
        "net_tax": net_tax,
        "warning": "This generic reconciliation does not apply minimum tax, limitation, surcharge, exemption, or filing rules unless supplied as explicit lines.",
    }


def vat(payload: dict[str, Any]) -> dict[str, Any]:
    places = precision(payload)
    amount = dec(payload.get("amount"), "amount")
    rate = dec(payload.get("rate"), "rate")
    inclusive = payload.get("inclusive", False)
    if not isinstance(inclusive, bool):
        raise InputError("inclusive must be boolean")
    if amount < 0 or rate < 0:
        raise InputError("amount and rate must be non-negative")
    if inclusive:
        gross = rnd(amount, places)
        net = rnd(amount / (Decimal(1) + rate), places)
        tax = rnd(gross - net, places)
    else:
        net = rnd(amount, places)
        tax = rnd(net * rate, places)
        gross = rnd(net + tax, places)
    return {
        "net_amount": net,
        "tax_amount": tax,
        "gross_amount": gross,
        "rate": rate,
        "inclusive_input": inclusive,
        "invariants": {"net_plus_tax_equals_gross": rnd(net + tax, places) == gross},
        "warning": "Rate, exemption, withholding, and deduction eligibility must be independently verified.",
    }


def day_count(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        start = date.fromisoformat(str(payload.get("start_date")))
        end = date.fromisoformat(str(payload.get("end_date")))
    except ValueError as exc:
        raise InputError("start_date and end_date must be ISO dates") from exc
    if end < start:
        raise InputError("end_date must not be before start_date")
    basis = payload.get("basis", "actual")
    actual_days = (end - start).days
    if basis == "actual":
        count = actual_days
    elif basis == "30E/360":
        d1 = min(start.day, 30)
        d2 = min(end.day, 30)
        count = (end.year - start.year) * 360 + (end.month - start.month) * 30 + d2 - d1
    else:
        raise InputError("basis must be actual or 30E/360")
    return {"start_date": start, "end_date": end, "basis": basis, "day_count": count, "actual_days": actual_days}


OPERATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "journal-check": journal_check,
    "straight-line-depreciation": straight_line_depreciation,
    "declining-balance-depreciation": declining_balance_depreciation,
    "present-value": present_value,
    "effective-interest": effective_interest,
    "weighted-average-inventory": weighted_average_inventory,
    "fifo-inventory": fifo_inventory,
    "fx-valuation": fx_valuation,
    "index-restatement": index_restatement,
    "impairment": impairment,
    "deferred-tax": deferred_tax,
    "tax-reconciliation": tax_reconciliation,
    "vat": vat,
    "day-count": day_count,
}


EXAMPLES: dict[str, dict[str, Any]] = {
    "journal-check": {"precision": 2, "entries": [{"account": "100", "debit": "120.00", "credit": "0"}, {"account": "600", "debit": "0", "credit": "100.00"}, {"account": "391", "debit": "0", "credit": "20.00"}]},
    "straight-line-depreciation": {"cost": "1000", "residual_value": "100", "life_periods": 3, "precision": 2},
    "declining-balance-depreciation": {"cost": "1000", "residual_value": "100", "rate": "0.40", "life_periods": 3, "precision": 2},
    "present-value": {"rate": "0.10", "cashflows": [{"period": 1, "amount": "110"}], "precision": 2},
    "effective-interest": {"initial_carrying_amount": "1000", "rate": "0.10", "payments": ["300", "300", "631"], "precision": 2},
    "weighted-average-inventory": {"opening_quantity": "10", "opening_unit_cost": "100", "transactions": [{"type": "purchase", "quantity": "10", "unit_cost": "120"}, {"type": "sale", "quantity": "5"}], "precision": 2},
    "fifo-inventory": {"opening_layers": [{"quantity": "10", "unit_cost": "100"}], "transactions": [{"type": "purchase", "quantity": "10", "unit_cost": "120"}, {"type": "sale", "quantity": "12"}], "precision": 2},
    "fx-valuation": {"foreign_amount": "1000", "book_rate": "30.00", "closing_rate": "32.00", "precision": 2},
    "index-restatement": {"amount": "1000", "base_index": "2000", "closing_index": "2500", "precision": 2},
    "impairment": {"carrying_amount": "1000", "value_in_use": "820", "fair_value_less_disposal_costs": "780", "precision": 2},
    "deferred-tax": {"position_type": "asset", "carrying_amount": "1000", "tax_base": "800", "tax_rate": "0.25", "precision": 2},
    "tax-reconciliation": {"accounting_profit": "1000", "additions": [{"description": "KKEG örneği", "amount": "100", "difference_type": "permanent"}], "deductions": [{"description": "İndirim örneği", "amount": "50", "difference_type": "permanent"}], "loss_carryforwards_used": "0", "tax_rate": "0.25", "tax_credits": "0", "precision": 2},
    "vat": {"amount": "120", "rate": "0.20", "inclusive": True, "precision": 2},
    "day-count": {"start_date": "2026-01-01", "end_date": "2026-02-01", "basis": "actual"},
}


def load_payload(path_text: str) -> dict[str, Any]:
    if path_text == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path_text).read_text(encoding="utf-8")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise InputError("input JSON root must be an object")
    return payload


def envelope(operation: str, payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return decimal_json(
        {
            "engine": "muhasebecim_engine",
            "engine_version": ENGINE_VERSION,
            "python_version": platform.python_version(),
            "decimal_precision": getcontext().prec,
            "rounding": str(getcontext().rounding),
            "operation": operation,
            "input_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
            "source_inputs": payload.get("sources", []),
            "result": result,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", nargs="?", choices=sorted(OPERATIONS))
    parser.add_argument("--input", default="-", help="UTF-8 JSON input path, or - for stdin")
    parser.add_argument("--output", help="UTF-8 JSON output path")
    parser.add_argument("--list", action="store_true", help="list operations")
    parser.add_argument("--example", action="store_true", help="print an example input for the selected operation")
    args = parser.parse_args()

    if args.list:
        print(json.dumps({"operations": sorted(OPERATIONS)}, ensure_ascii=False, indent=2))
        return 0
    if not args.operation:
        parser.error("operation is required unless --list is used")
    if args.example:
        print(json.dumps(EXAMPLES[args.operation], ensure_ascii=False, indent=2))
        return 0

    try:
        payload = load_payload(args.input)
        result = OPERATIONS[args.operation](payload)
        output = envelope(args.operation, payload, result)
        text = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0
    except (InputError, OSError) as exc:
        error = {"error": type(exc).__name__, "message": str(exc), "operation": args.operation}
        sys.stderr.write(json.dumps(error, ensure_ascii=False) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
