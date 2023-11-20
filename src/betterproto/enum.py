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


class EnumType(EnumMeta):
    _value_map_: Mapping[int, Enum]
    _member_map_: Mapping[str, Enum]

    def __new__(
        mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]
    ) -> Self:
        value_map = {}
        member_map = {}

        new_mcs = type(
            f"{name}Type",
            tuple(
                dict.fromkeys(
                    [base.__class__ for base in bases if base.__class__ is not type]
                    + [EnumType, type]
                )
            ),  # reorder the bases so EnumType and type are last to avoid conflicts
            {"_value_map_": value_map, "_member_map_": member_map},
        )

        members = {
            name: value
            for name, value in namespace.items()
            if not _is_descriptor(value) and not name.startswith("__")
        }

        cls = type.__new__(
            new_mcs,
            name,
            bases,
            {key: value for key, value in namespace.items() if key not in members},
        )
        # this allows us to disallow member access from other members as
        # members become proper class variables

        for name, value in members.items():
            member = value_map.get(value)
            if member is None:
                member = cls.__new__(cls, name=name, value=value)  # type: ignore
                value_map[value] = member
            member_map[name] = member
            type.__setattr__(new_mcs, name, member)

        return cls


    def __repr__(cls) -> str:
        return f"<enum {cls.__name__!r}>"

    def __len__(cls) -> int:
        return len(cls._member_map_)

    def __setattr__(cls, name: str, value: Any) -> Never:
        raise AttributeError(f"{cls.__name__}: cannot reassign Enum members.")

    def __delattr__(cls, name: str) -> Never:
        raise AttributeError(f"{cls.__name__}: cannot delete Enum members.")

    def __contains__(cls, member: object) -> bool:
        return isinstance(member, cls) and member.name in cls._member_map_


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
        except (KeyError, TypeError):
            return cls.__new__(cls, name=None, value=value)

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
