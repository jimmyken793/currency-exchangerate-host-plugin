"""Fetch exchange rates from exchangerate.host.

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
    """Currency exchange plugin backed by exchangerate.host."""

    TITLE = "Currency Exchange Rate Host Plugin"
    NAME = "CurrencyexchangerateatehostPlugin"
    # Keep this slug for compatibility with the existing InvenTree database.
    SLUG = "currency-exchangerateate--host-plugin"
    DESCRIPTION = "Fetch exchange rate from exchangerate.host"
    VERSION = PLUGIN_VERSION

    AUTHOR = "Jimmy Cheng"
    WEBSITE = "https://github.com/jimmyken793/currency-exchangerate-host-plugin"
    LICENSE = "MIT"

    SETTINGS = {
        "API_TOKEN": {
            "name": "API token",
            "description": "API token to access exchangerate.host",
            "default": "",
            "protected": True,
        }
    }

    def update_exchange_rates(self, base_currency: str, symbols: list[str]) -> dict:
        """Request exchange rate data from external API."""
        token = self.get_setting("API_TOKEN")

        if not token:
            logger.error("No API token provided for %s", self.NAME)
            return {}

        response = self.api_call(
            "live",
            url_args={"access_key": token, "source": [base_currency]},
            simple_response=False,
        )

        if response.status_code == 200:
            success = response.json().get("success", False)
            if success:
                raw_rates = response.json().get("quotes", {})
                rates = {}

                # exchangerate.host returns quote keys such as "USDTWD".
                for key, value in raw_rates.items():
                    if key.startswith(base_currency):
                        rates[key[len(base_currency) :]] = value

                rates[base_currency] = 1.00
                return rates

        logger.warning(
            "Failed to update exchange rates from %s: Server returned status %s",
            self.api_url,
            response.status_code,
        )
        return {}

    @property
    def api_url(self):
        """Return the API URL for this plugin."""
        return "http://api.exchangerate.host"
