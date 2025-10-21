import asyncio
from typing import Optional, Union

from livekit import rtc
from livekit.agents import llm
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    model_config = {"arbitrary_types_allowed": True}


class CallRoom(rtc.Room):
    def __init__(self, name: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self._name = name
        super().__init__(loop=loop)

    @property
    def name(self) -> str:
        return self._name


class CallSessionStarterConfigRealtime(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    llm: Union[llm.LLM, llm.RealtimeModel]
    user_away_timeout: float
    use_tts_aligned_transcript: bool
    preemptive_generation: bool
