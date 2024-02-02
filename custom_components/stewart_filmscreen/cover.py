"""Cover entity that implements motor control."""

import logging

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from stewartfilmscreenclient import StewartFilmscreenClient
from stewartfilmscreenclient.protocol import StewartFilmscreenProtocol

from .const import DOMAIN, ATTR_MANUFACTURER, ATTR_MODEL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup Stewart Filmscreen Covers from a config entry."""
    cvm_client = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    reverse = True

    assert unique_id is not None

    covers = []
    for motor in (
        StewartFilmscreenProtocol.MOTOR_A,
        StewartFilmscreenProtocol.MOTOR_B,
        StewartFilmscreenProtocol.MOTOR_C,
        StewartFilmscreenProtocol.MOTOR_D,
    ):
        cover = StewartFilmscreenCoverEntity(
            unique_id,
            f"{unique_id}_{motor}",
            cvm_client,
            motor,
            (reverse := not reverse),
        )
        covers.append(cover)

    async_add_entities(covers)


class StewartFilmscreenCoverEntity(CoverEntity):
    """Cover entity class implenting motor control"""

    def __init__(
        self,
        device_id: str,
        unique_id: str,
        cvm_client: StewartFilmscreenClient,
        motor: str,
        reverse: bool,
    ):
        # Initialize cover for motor
        self._name = f"{ATTR_MANUFACTURER} {ATTR_MODEL} {motor}"
        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})

        self._cvm_client = cvm_client
        self._motor = motor
        self._reverse = reverse

        self._is_closed = None
        self._is_closing = False
        self._is_opening = False
        self._position = None

        # register to recieve state messages from cvm
        self._cvm_client.register_state_message_callback(
            self._async_handle_cvm_client_state_messages
        )

    async def async_added_to_hass(self):
        await self._cvm_client.async_send_command(
            StewartFilmscreenProtocol.query(
                self._motor, StewartFilmscreenProtocol.QUERY_POSITION
            )
        )

    async def _async_handle_cvm_client_state_messages(self, state_message):
        if (
            state_message.get("type") == StewartFilmscreenProtocol.TYPE_EVENT
            and state_message.get("motor") == self._motor
        ):

            _LOGGER.debug("Received event from CVM: %s", state_message)

            if (
                state_message.get(StewartFilmscreenProtocol.TYPE_EVENT)
                == StewartFilmscreenProtocol.EVENT_STATUS
            ):
                status_map = {
                    StewartFilmscreenProtocol.STATUS_STOP: self._set_stop,
                    StewartFilmscreenProtocol.STATUS_RETRACTING: self._set_retracting,
                    StewartFilmscreenProtocol.STATUS_EXTENDING: self._set_extending,
                    StewartFilmscreenProtocol.STATUS_HOME: self._set_home,
                    StewartFilmscreenProtocol.STATUS_END: self._set_end,
                }

                status_map.get(state_message.get("value"))()

            if (
                state_message.get(StewartFilmscreenProtocol.TYPE_EVENT)
                == StewartFilmscreenProtocol.EVENT_POSITION
            ):
                position = round(float(state_message.get("value")))
                position = min(position, 100)

                self._set_position(position)

            self.async_write_ha_state()

    def _set_stop(self):
        self._is_closing = False
        self._is_opening = False

    def _set_retracting(self):
        self._is_closed = False
        self._is_closing = False
        self._is_opening = True

    def _set_extending(self):
        self._is_closed = False
        self._is_closing = True
        self._is_opening = False

    def _set_home(self):
        self._is_closed = False
        self._is_closing = False
        self._is_opening = False
        self._set_position(0)

    def _set_end(self):
        self._is_closed = True
        self._is_closing = False
        self._is_opening = False
        self._set_position(100)

    def _set_position(self, position):
        if not self._is_closing and not self._is_opening:
            self._is_closed = position == 100

        self._position = 100 - position

    async def async_will_remove_from_hass(self):
        self._cvm_client.deregister_state_message_callback(
            self._async_handle_cvm_client_state_messages
        )

    @property
    def available(self):
        """Return if Stewart Filsmscreen CVM is available."""
        return self._cvm_client.is_connected

    @property
    def name(self):
        """Return the name of the cover"""
        return self._name

    @property
    def is_closed(self):
        """Return True if the cover is closed"""
        return self._is_closed

    @property
    def is_opening(self):
        """Return True if the cover is opening"""
        return self._is_opening

    @property
    def is_closing(self):
        """Return True if the cover is closing"""
        return self._is_closing

    @property
    def current_cover_position(self):
        """Return the current position of the cover"""
        return self._position

    @property
    def supported_features(self):
        """Bitmask of features supported by the cover"""
        return (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

    async def async_open_cover(self, **kwargs):
        """Asynchronously open the cover"""
        command = StewartFilmscreenProtocol.COMMAND_UP
        if self._reverse:
            command = StewartFilmscreenProtocol.COMMAND_DOWN

        await self._cvm_client.async_send_command(
            StewartFilmscreenProtocol.command(self._motor, command)
        )

    async def async_close_cover(self, **kwargs):
        """Asynchronously close the cover"""
        command = StewartFilmscreenProtocol.COMMAND_DOWN
        if self._reverse:
            command = StewartFilmscreenProtocol.COMMAND_UP

        await self._cvm_client.async_send_command(
            StewartFilmscreenProtocol.command(self._motor, command)
        )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover movement"""
        await self._cvm_client.async_send_command(
            StewartFilmscreenProtocol.command(
                self._motor, StewartFilmscreenProtocol.COMMAND_STOP
            )
        )
