from enum import Enum


class AttributesScope(str, Enum):
    SERVER_SCOPE = 'SERVER_SCOPE'
    SHARED_SCOPE = 'SHARED_SCOPE'
    CLIENT_SCOPE = 'CLIENT_SCOPE'
