"""Fetch exchange rates from Frankfurter v2.

This plugin is derived from InvenTree's built-in currency exchange plugin,
which is distributed under the MIT license.
"""

import logging

from plugin import InvenTreePlugin
from plugin.mixins import APICallMixin, CurrencyExchangeMixin, SettingsMixin

from . import PLUGIN_VERSION

logger = logging.getLogger("inventree")


class CurrencyexchangerateatehostPlugin(
    APICallMixin, CurrencyExchangeMixin, SettingsMixin, InvenTreePlugin
):
    """Currency exchange plugin backed by Frankfurter v2."""

    TITLE = "Frankfurter v2 Currency Exchange Plugin"
    NAME = "CurrencyexchangerateatehostPlugin"
    # Keep this slug for compatibility with the existing InvenTree database.
    SLUG = "currency-exchangerateate--host-plugin"
    DESCRIPTION = "Fetch exchange rates from Frankfurter v2"
    VERSION = PLUGIN_VERSION

    AUTHOR = "Jimmy Cheng"
    WEBSITE = "https://github.com/jimmyken793/currency-exchangerate-host-plugin"
    LICENSE = "MIT"

    SETTINGS = {
        "API_TOKEN": {
            "name": "API token (deprecated)",
            "description": "Deprecated and unused. Frankfurter v2 does not require an API token.",
            "default": "",
            "protected": True,
        }
    }

    def update_exchange_rates(self, base_currency: str, symbols: list[str]) -> dict:
        """Request exchange rate data from external API."""
        response = self.api_call(
            "rates",
            url_args={"base": base_currency, "quotes": symbols},
            simple_response=False,
        )

        if response.status_code == 200:
            payload = response.json()
            rates = {base_currency: 1.00}

            if isinstance(payload, list):
                for item in payload:
                    quote = item.get("quote")
                    rate = item.get("rate")

                    if quote and rate is not None:
                        rates[quote] = rate

                missing_symbols = set(symbols) - set(rates)

                if missing_symbols:
                    logger.warning(
                        "Frankfurter v2 did not return exchange rates for: %s",
                        ", ".join(sorted(missing_symbols)),
                    )

                return rates

            logger.warning(
                "Invalid exchange rate data returned from %s: expected list, got %s",
                self.api_url,
                type(payload),
            )
            return {}

        logger.warning(
            "Failed to update exchange rates from %s: Server returned status %s",
            self.api_url,
            response.status_code,
        )
        return {}

    @property
    def api_url(self):
        """Return the API URL for this plugin."""
        return "https://api.frankfurter.dev/v2"
