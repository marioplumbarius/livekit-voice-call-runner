from livekit.agents import Agent, ChatMessage

from livekit_voice_call_runner.logger import CallLogger


class CallAgent(Agent):
    def __init__(self, instructions: str, logger: CallLogger):
        super().__init__(instructions=instructions)
        self._logger = logger

    async def on_chat_message_added(self, chat_message: ChatMessage) -> None: ...
