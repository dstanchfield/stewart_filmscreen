"""Dispatches all commands and events to and from the CVM client."""

import logging

from stewartfilmscreenclient import StewartFilmscreenClient
from stewartfilmscreenclient.protocol import StewartFilmscreenProtocol

_LOGGER = logging.getLogger(__name__)


class DeviceDispatch:
    """Device dispatch class implenting CVM command and event dispatching"""

    def __init__(
        self,
        cvm_client: StewartFilmscreenClient,
    ):
        self._cvm_client = cvm_client
        self._state_message_dispatch = {}

        # register to recieve state messages from cvm
        self._cvm_client.register_state_message_callback(
            self._async_handle_cvm_client_state_messages
        )

    async def _async_handle_cvm_client_state_messages(self, state_message):
        _LOGGER.debug("Received state message from CVM: %s", state_message)

        for motor in (
            StewartFilmscreenProtocol.MOTOR_ALL,
            StewartFilmscreenProtocol.MOTOR_A,
            StewartFilmscreenProtocol.MOTOR_B,
            StewartFilmscreenProtocol.MOTOR_C,
            StewartFilmscreenProtocol.MOTOR_D,
        ):
            if motor == state_message.get("motor"):
                if (handler := self._state_message_dispatch.get(motor)) is not None:
                    await handler(state_message)

    def register_dispatched_state_message(self, motor, handler):
        """Registers callbacks to be called for specific motors."""
        self._state_message_dispatch[motor] = handler

    def is_connected(self):
        """Provides dispatched CVM connection status."""
        return self._cvm_client.is_connected()

    async def async_send_command(self, command):
        """Cover entity class implenting motor control"""
        await self._cvm_client.async_send_command(command)

    def close(self):
        """Closed CVM client and performs cleanup."""
        self._cvm_client.deregister_state_message_callback(
            self._async_handle_cvm_client_state_messages
        )
        self._cvm_client.close()
        self._state_message_dispatch = {}
