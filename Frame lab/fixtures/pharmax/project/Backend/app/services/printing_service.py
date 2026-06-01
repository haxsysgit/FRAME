"""
ESC/POS Printing Service for Pharmax

Handles thermal receipt printer output for invoices, receipts, and reports.
Adapts the existing receipt layout to plain text suitable for ESC/POS printers.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from example_projects.pharmax.Backend.app.core import config as cfg

logger = logging.getLogger(__name__)


class PrinterConnectionError(Exception):
    """Raised when printer connection fails."""
    pass


class PrintingService:
    """Service for ESC/POS thermal printing."""

    RECEIPT_WIDTH = 42  # Characters for 80mm paper

    @staticmethod
    def _get_printer():
        """
        Initialize printer based on config.
        Returns None if printer unavailable (allows graceful degradation).
        """
        try:
            if cfg.PRINTER_TYPE == "usb":
                from escpos.printer import Usb
                return Usb(cfg.USB_VENDOR_ID, cfg.USB_PRODUCT_ID)
            else:
                from escpos.printer import Network
                return Network(cfg.PRINTER_IP, port=cfg.PRINTER_PORT)
        except Exception as e:
            logger.warning(f"Printer connection failed: {e}")
            return None

    @staticmethod
    def _printer_target() -> str:
        if cfg.PRINTER_TYPE == "usb":
            return f"usb:{hex(cfg.USB_VENDOR_ID)}:{hex(cfg.USB_PRODUCT_ID)}"
        return f"network:{cfg.PRINTER_IP}:{cfg.PRINTER_PORT}"

    @staticmethod
    def center(text: str, width: int = 42) -> str:
        """Center text within receipt width."""
        return text.center(width)

    @staticmethod
    def line(char: str = "-", width: int = 42) -> str:
        """Create a horizontal line."""
        return char * width

    @staticmethod
    def format_currency(amount: float | Decimal | None) -> str:
        """Format amount as currency string."""
        if amount is None:
            return "0.00"
        return f"{float(amount):,.2f}"

    @staticmethod
    def format_date(dt: datetime | str | None) -> str:
        """Format datetime for receipt."""
        if dt is None:
            return "—"
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                return dt
        return dt.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def build_receipt_text(
        cls,
        invoice: dict[str, Any],
        pharmacy_name: str = "Pharmax Pharmacy",
        footer_text: str = "Thank you for your patronage!",
        show_tax: bool = False,
        tax_amount: float = 0.0,
    ) -> str:
        """
        Build plain text receipt from invoice data.
        Preserves the existing receipt layout structure.

        Args:
            invoice: Invoice dict with items, total_amount, payment_method, etc.
            pharmacy_name: Store name for header
            footer_text: Custom footer message
            show_tax: Whether to display tax line
            tax_amount: Tax amount if applicable

        Returns:
            Formatted receipt text ready for ESC/POS printing
        """
        def _to_float(value: Any) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        w = cls.RECEIPT_WIDTH
        lines = []

        # Header
        lines.append(cls.center(pharmacy_name.upper(), w))
        lines.append(cls.center("RECEIPT", w))
        lines.append(cls.line("=", w))
        lines.append("")

        # Meta info
        inv_id = invoice.get("id", "")[:12]
        created_at = cls.format_date(invoice.get("created_at"))
        printed_at = cls.format_date(datetime.now())
        sold_by_name = invoice.get("sold_by_name") or invoice.get("name") or "—"
        payment = invoice.get("payment_method") or "—"

        lines.append(f"Date: {created_at}")
        lines.append(f"Sold By: {sold_by_name}")
        lines.append(f"Payment: {payment}")
        lines.append(f"Invoice #: {inv_id}")
        lines.append(f"Printed At: {printed_at}")
        lines.append(cls.line("-", w))

        # Column header: Item | Qty | Price | Total
        header = f"{'Item':<18} {'Qty':>4} {'Price':>8} {'Total':>8}"
        lines.append(header)
        lines.append(cls.line("-", w))

        # Items
        items = invoice.get("items") or []
        subtotal_value = 0.0
        for item in items:
            product = item.get("product") or {}
            unit = item.get("product_unit") or {}

            name = product.get("name", "")[:18]
            unit_name = unit.get("name", "")
            qty = item.get("quantity", 0)
            price = cls.format_currency(item.get("unit_price"))
            line_total_value = _to_float(item.get("line_total"))
            if line_total_value <= 0:
                line_total_value = _to_float(item.get("quantity")) * _to_float(item.get("unit_price"))
            subtotal_value += line_total_value
            line_total = cls.format_currency(line_total_value)

            # Main item line
            line = f"{name:<18} {qty:>4} {price:>8} {line_total:>8}"
            lines.append(line)

            # Unit name on second line if present
            if unit_name:
                lines.append(f"  ({unit_name})")

        lines.append(cls.line("-", w))

        # Tax line (optional)
        if show_tax and tax_amount > 0:
            tax_str = cls.format_currency(tax_amount)
            lines.append(f"{'Tax:':<30} {tax_str:>10}")

        # Total
        total_amount_value = _to_float(invoice.get("total_amount"))
        payment_label = str(payment).upper()
        discount_value = max(subtotal_value - total_amount_value, 0.0)
        credit_value = max(total_amount_value, 0.0) if "CREDIT" in payment_label else max(total_amount_value - subtotal_value, 0.0)

        subtotal_amount = cls.format_currency(subtotal_value)
        discount_amount = cls.format_currency(discount_value)
        credit_amount = cls.format_currency(credit_value)
        total_amount = cls.format_currency(total_amount_value)

        lines.append(f"{'Subtotal:':<30} {subtotal_amount:>10}")
        lines.append(f"{'Discount:':<30} {discount_amount:>10}")
        lines.append(f"{'Credit:':<30} {credit_amount:>10}")
        lines.append(cls.line("=", w))
        lines.append(f"{'TOTAL:':<30} {total_amount:>10}")
        lines.append(cls.line("=", w))
        lines.append("")

        # Footer
        lines.append(cls.center(footer_text, w))
        lines.append(cls.center("Your health is our priority", w))
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def print_receipt(
        cls,
        invoice: dict[str, Any],
        pharmacy_name: str = "Pharmax Pharmacy",
        footer_text: str = "Thank you for your patronage!",
        show_tax: bool = False,
        tax_amount: float = 0.0,
    ) -> dict[str, Any]:
        """
        Print invoice receipt to ESC/POS printer.

        Args:
            invoice: Invoice data dict
            pharmacy_name: Store name
            footer_text: Custom footer
            show_tax: Show tax line
            tax_amount: Tax amount

        Returns:
            Result dict with success status and message
        """
        receipt_text = cls.build_receipt_text(
            invoice=invoice,
            pharmacy_name=pharmacy_name,
            footer_text=footer_text,
            show_tax=show_tax,
            tax_amount=tax_amount,
        )

        printer = cls._get_printer()
        if printer is None:
            return {
                "success": False,
                "error": f"Printer not available ({cls._printer_target()})",
                "receipt_text": receipt_text,
            }

        try:
            printer.text(receipt_text)
            printer.cut()
            return {
                "success": True,
                "message": "Receipt printed successfully",
                "receipt_text": receipt_text,
            }
        except Exception as e:
            logger.error(f"Print failed: {e}")
            return {
                "success": False,
                "error": f"{e} ({cls._printer_target()})",
                "receipt_text": receipt_text,
            }
        finally:
            try:
                printer.close()
            except Exception:
                pass

    @classmethod
    def build_daily_summary_text(
        cls,
        summary: dict[str, Any],
        pharmacy_name: str = "Pharmax Pharmacy",
    ) -> str:
        """
        Build daily reconciliation summary receipt.

        Args:
            summary: Dict with total_cash, total_pos, total_transfer, revenue, etc.

        Returns:
            Formatted summary text for ESC/POS
        """
        w = cls.RECEIPT_WIDTH
        lines = []

        lines.append(cls.center(pharmacy_name.upper(), w))
        lines.append(cls.center("DAILY RECONCILIATION", w))
        lines.append(cls.center(datetime.now().strftime("%Y-%m-%d"), w))
        lines.append(cls.line("=", w))
        lines.append("")

        # Payment breakdown
        lines.append("PAYMENT BREAKDOWN")
        lines.append(cls.line("-", w))
        cash = cls.format_currency(summary.get("total_cash", 0))
        pos = cls.format_currency(summary.get("total_pos", 0))
        transfer = cls.format_currency(summary.get("total_transfer", 0))

        lines.append(f"{'Cash:':<25} {cash:>15}")
        lines.append(f"{'POS:':<25} {pos:>15}")
        lines.append(f"{'Transfer:':<25} {transfer:>15}")
        lines.append(cls.line("-", w))

        # Revenue
        revenue = cls.format_currency(summary.get("total_revenue", 0))
        lines.append(f"{'TOTAL REVENUE:':<25} {revenue:>15}")
        lines.append(cls.line("=", w))

        # Invoice counts
        lines.append("")
        lines.append("INVOICE COUNTS")
        lines.append(cls.line("-", w))
        lines.append(f"{'Stamped:':<25} {summary.get('stamped_count', 0):>15}")
        lines.append(f"{'Dispensed:':<25} {summary.get('dispensed_count', 0):>15}")
        lines.append(f"{'Cancelled:':<25} {summary.get('cancelled_count', 0):>15}")
        lines.append(cls.line("=", w))
        lines.append("")

        lines.append(cls.center("End of Report", w))
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def print_daily_summary(
        cls,
        summary: dict[str, Any],
        pharmacy_name: str = "Pharmax Pharmacy",
    ) -> dict[str, Any]:
        """Print daily reconciliation summary."""
        text = cls.build_daily_summary_text(summary, pharmacy_name)

        printer = cls._get_printer()
        if printer is None:
            return {
                "success": False,
                "error": f"Printer not available ({cls._printer_target()})",
                "summary_text": text,
            }

        try:
            printer.text(text)
            printer.cut()
            return {
                "success": True,
                "message": "Summary printed successfully",
                "summary_text": text,
            }
        except Exception as e:
            logger.error(f"Print failed: {e}")
            return {
                "success": False,
                "error": f"{e} ({cls._printer_target()})",
                "summary_text": text,
            }
        finally:
            try:
                printer.close()
            except Exception:
                pass
