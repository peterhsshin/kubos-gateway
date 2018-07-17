import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class SatConnectionProtocol:
    def __init__(self, loop, service):
        self.loop = loop
        self.transport = None
        self.service = service

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        asyncio.ensure_future(self.service.message_received(json.loads(data.decode())))
        # self.transport.close()

    # TODO: "[Errno 61] Connection refused" never gets fed back to Major Tom.
    def error_received(self, exc):
        logger.info('Error received: {}'.format(exc))

    def connection_lost(self, exc):
        logger.info("Socket closed")
        # self.loop.call_later(5, SatConnection.connect_to_sat())


class SatService:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.transport = None
        self.protocol = None
        self.satellite = None

    async def connect(self):
        logger.info(f'Connecting to the {self.name} sat service')
        loop = asyncio.get_event_loop()
        self.transport, self.protocol = await loop.create_datagram_endpoint(lambda: SatConnectionProtocol(loop, self),
                                                                            remote_addr=(self.satellite.host, self.port))

    async def message_received(self, message):
        logger.warning("Unhandled message_received!")

    # No special match needed-- the default behavior will trigger and route by subsystem.
    def match(self, command):
        return False