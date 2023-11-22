from __future__ import annotations

import sys
from enum import (
    EnumMeta,
    IntEnum,
)
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Tuple,
)


if TYPE_CHECKING:
    from collections.abc import (
        Generator,
        Mapping,
    )

    from typing_extensions import (
        Never,
        Self,
    )


def _is_descriptor(obj: object) -> bool:
    return (
        hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")
    )


class Enum(IntEnum):
    """
    The base class for protobuf enumerations, all generated enumerations will
    inherit from this. Emulates `enum.IntEnum`.
    """

    @classmethod
    def try_value(cls, value: int = 0) -> Self:
        """Return the value which corresponds to the value.

        Parameters
        -----------
        value: :class:`int`
            The value of the enum member to get.

        Returns
        -------
        :class:`Enum`
            The corresponding member or a new instance of the enum if
            ``value`` isn't actually a member.
        """
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def from_string(cls, name: str) -> Self:
        """Return the value which corresponds to the string name.

        Parameters
        -----------
        name: :class:`str`
            The name of the enum member to get.

        Raises
        -------
        :exc:`ValueError`
            The member was not found in the Enum.
        """
        try:
            return cls._member_map_[name]
        except KeyError as e:
            raise ValueError(f"Unknown value {name} for enum {cls.__name__}") from e
