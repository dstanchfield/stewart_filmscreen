"""The Stewart Filmscreen CVM integration."""

from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
import voluptuous as vol

from stewartfilmscreenclient import StewartFilmscreenClient

from .const import DOMAIN, ATTR_MANUFACTURER, ATTR_MODEL
from .exceptions import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.COVER]

RECALL_PRESET_SCHEMA = vol.Schema(
    {
        vol.Required("preset_number"): cv.positive_int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Stewart Filmscreen from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    device_registry = dr.async_get(hass)

    config = entry.data
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    cvm_client = StewartFilmscreenClient(host, port, username, password)

    try:
        auth_success = await cvm_client.async_connect()

        if not auth_success:
            raise InvalidAuth

        hass.data[DOMAIN][entry.entry_id] = cvm_client
    except (ConnectionRefusedError, TimeoutError) as error:
        _LOGGER.debug("Connection error: %s", error)
        raise CannotConnect from error

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        name=f"{ATTR_MANUFACTURER} {ATTR_MODEL}",
        manufacturer=ATTR_MANUFACTURER,
        model=ATTR_MODEL,
    )

    await setup_custom_services(hass, cvm_client)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def setup_custom_services(hass: HomeAssistant, cvm_client):
    """Setup recall and store services"""

    async def async_handle_recall_service(service: ServiceCall):
        preset_number = service.data["preset_number"]
        await cvm_client.async_recall_preset(preset_number)

    async def async_handle_store_service(service: ServiceCall):
        preset_number = service.data["preset_number"]
        await cvm_client.async_store_preset(preset_number)

    hass.services.async_register(
        DOMAIN,
        "recall_preset",
        async_handle_recall_service,
        schema=RECALL_PRESET_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, "store_preset", async_handle_store_service, schema=RECALL_PRESET_SCHEMA
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        cvm_client = hass.data[DOMAIN][entry.entry_id]
        cvm_client.close()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
