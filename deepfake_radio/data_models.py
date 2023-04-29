
from dataclasses import dataclass
from typing import Optional

@dataclass
class Source:
    location: Optional[str] = None
    type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

@dataclass
class VoiceClip:
    name: str
    idx: int
    description: Optional[str] = None
    source: Optional[Source] = None
    isolate: Optional[bool] = None
    clip_size: Optional[int] = None

@dataclass
class Voice:
    name: str
    description: Optional[str] = None
    clips: Optional[list[VoiceClip]] = None
