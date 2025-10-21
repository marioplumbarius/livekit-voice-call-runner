from livekit import rtc

# NOTE: keep this in sync with livekit/rtc/_proto/participant_pb2.pyi:99
_REASON_TO_NAME_MAP = {
    "0": "UNKNOWN_REASON",
    "1": "CLIENT_INITIATED",
    "2": "DUPLICATE_IDENTITY",
    "3": "SERVER_SHUTDOWN",
    "4": "PARTICIPANT_REMOVED",
    "5": "ROOM_DELETED",
    "6": "STATE_MISMATCH",
    "7": "JOIN_FAILURE",
    "8": "MIGRATION",
    "9": "SIGNAL_CLOSE",
    "10": "ROOM_CLOSED",
    "11": "USER_UNAVAILABLE",
    "12": "USER_REJECTED",
    "13": "SIP_TRUNK_FAILURE",
    "14": "CONNECTION_TIMEOUT",
    "15": "MEDIA_FAILURE",
}


def map_to_name(reason: rtc.DisconnectReason) -> str:
    return _REASON_TO_NAME_MAP.get(str(reason), "INVALID_REASON")
