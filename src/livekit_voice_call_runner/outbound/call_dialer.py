from livekit import api
from livekit.protocol import sip

from livekit_voice_call_runner.core.ishutdown import IShutdown
from livekit_voice_call_runner.logger import CallLogger


class CallDialer(IShutdown):
    def __init__(self, livekit_api: api.LiveKitAPI, logger: CallLogger):
        self._livekit_api = livekit_api
        self._logger = logger

    async def dial(self, request: sip.CreateSIPParticipantRequest) -> api.SIPParticipantInfo:
        logger_extra = {
            "sip_trunk_id": request.sip_trunk_id,
            "sip_call_to": request.sip_call_to,
            "sip_number": request.sip_number,
            "room_name": request.room_name,
            "dtmf": request.dtmf,
        }
        self._logger.info("Dialing call.", extra=logger_extra)
        response = await self._livekit_api.sip.create_sip_participant(create=request)
        self._logger.info(
            "Successfully dialed call.",
            extra={**logger_extra, "sip_call_id": response.sip_call_id},
        )
        return response

    async def shutdown(self) -> None:
        self._logger.info("Shutting down.")
        await self._livekit_api.aclose()
        self._logger.info("Successfully shut down.")
