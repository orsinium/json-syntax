import pytest
from tests.common import Rules
from unittest.mock import Mock

from json_syntax import std
from json_syntax.helpers import JSON2PY, PY2JSON, INSP_PY, INSP_JSON, NoneType
from json_syntax.string import stringify_keys

from datetime import datetime, date
from decimal import Decimal
from enum import Enum, IntEnum
import math
from typing import Optional, Union, Tuple, List, Set, FrozenSet, Dict
from pickle import dumps

try:
    from typing import OrderedDict  # 3.7.2
except ImportError:
    OrderedDict = None


Mystery = Tuple["Mystery", "Thing"]


def test_atoms_disregard():
    "Test the atoms rule will disregard unknown types and verbs."

    assert std.atoms(verb="unknown", typ=str, ctx=Rules()) is None
    for verb in (JSON2PY, PY2JSON, INSP_PY, INSP_JSON):
        assert std.atoms(verb=verb, typ=Mystery, ctx=Rules()) is None


def test_atoms_str():
    "Test the atoms rule will generate encoders and decoders for strings."

    decoder = std.atoms(verb=JSON2PY, typ=str, ctx=Rules())
    assert decoder("some string") == "some string"

    encoder = std.atoms(verb=PY2JSON, typ=str, ctx=Rules())
    assert encoder("some string") == "some string"

    inspect = std.atoms(verb=INSP_PY, typ=str, ctx=Rules())
    assert inspect("string")
    assert not inspect(5)

    inspect = std.atoms(verb=INSP_JSON, typ=str, ctx=Rules())
    assert inspect("string")
    assert not inspect(5)


def test_atoms_int():
    "Test the atoms rule will generate encoders and decoders for integers."

    decoder = std.atoms(verb=JSON2PY, typ=int, ctx=Rules())
    assert decoder(77) == 77

    encoder = std.atoms(verb=PY2JSON, typ=int, ctx=Rules())
    assert encoder(77) == 77

    inspect = std.atoms(verb=INSP_PY, typ=int, ctx=Rules())
    assert not inspect("string")
    assert inspect(5)

    inspect = std.atoms(verb=INSP_JSON, typ=int, ctx=Rules())
    assert not inspect("string")
    assert inspect(5)


def test_atoms_bool():
    "Test the atoms rule will generate encoders and decoders for booleans."

    decoder = std.atoms(verb=JSON2PY, typ=bool, ctx=Rules())
    assert decoder(False) is False
    assert decoder(True) is True

    encoder = std.atoms(verb=PY2JSON, typ=bool, ctx=Rules())
    assert encoder(False) is False
    assert encoder(True) is True

    inspect = std.atoms(verb=INSP_PY, typ=bool, ctx=Rules())
    assert not inspect("string")
    assert inspect(True)

    inspect = std.atoms(verb=INSP_JSON, typ=bool, ctx=Rules())
    assert not inspect("string")
    assert inspect(False)


def test_atoms_null():
    "Test the atoms rule will generate encoders and decoders for None / null."

    decoder = std.atoms(verb=JSON2PY, typ=NoneType, ctx=Rules())
    assert decoder(None) is None
    with pytest.raises(ValueError):
        decoder(5)

    encoder = std.atoms(verb=PY2JSON, typ=NoneType, ctx=Rules())
    assert encoder(None) is None
    with pytest.raises(ValueError):
        encoder(5)

    inspect = std.atoms(verb=INSP_PY, typ=NoneType, ctx=Rules())
    assert inspect(None)
    assert not inspect(0)

    inspect = std.atoms(verb=INSP_JSON, typ=NoneType, ctx=Rules())
    assert inspect(None)
    assert not inspect(0)


def test_atoms_picklable():
    "Test that actions generated by the atoms rule can be pickled."

    actions = [
        std.atoms(verb=verb, typ=typ, ctx=Rules())
        for verb in [JSON2PY, PY2JSON, INSP_PY, INSP_JSON]
        for typ in [str, int, bool, NoneType]
    ]
    assert None not in actions
    dumps(actions)


def test_floats_disregard():
    "Test the floats rule will disregard unknown types and verbs."

    assert std.floats(verb="unknown", typ=str, ctx=Rules()) is None
    for verb in (JSON2PY, PY2JSON, INSP_PY, INSP_JSON):
        assert std.floats(verb=verb, typ=Mystery, ctx=Rules()) is None


def test_floats():
    "Test the floats rule will generate encoders and decoders for floats that are tolerant of integers."

    decoder = std.floats(verb=JSON2PY, typ=float, ctx=Rules())
    assert decoder(77.7) == 77.7
    assert decoder(77) == 77.0
    assert math.isnan(decoder("nan"))
    assert math.isnan(decoder(float("nan")))

    encoder = std.floats(verb=PY2JSON, typ=float, ctx=Rules())
    assert encoder(77.7) == 77.7
    assert encoder(float("inf")) == float("inf")

    inspect = std.floats(verb=INSP_PY, typ=float, ctx=Rules())
    assert not inspect("string")
    assert not inspect("-inf")
    assert inspect(float("-inf"))
    assert not inspect(44)
    assert inspect(77.7)

    inspect = std.floats(verb=INSP_JSON, typ=float, ctx=Rules())
    assert not inspect("string")
    assert not inspect("-inf")
    assert inspect(float("-inf"))
    assert inspect(44)
    assert inspect(77.7)


def test_floats_nan_str():
    "Test the floats rule will generate encoders and decoders for floats that are tolerant of integers."

    decoder = std.floats_nan_str(verb=JSON2PY, typ=float, ctx=Rules())
    assert decoder(77.7) == 77.7
    assert decoder(77) == 77.0
    assert math.isnan(decoder("nan"))
    assert math.isnan(decoder(float("nan")))

    encoder = std.floats_nan_str(verb=PY2JSON, typ=float, ctx=Rules())
    assert encoder(77.7) == 77.7
    assert encoder(float("inf")) == "Infinity"

    inspect = std.floats_nan_str(verb=INSP_PY, typ=float, ctx=Rules())
    assert not inspect("string")
    assert not inspect("-inf")
    assert inspect(float("-inf"))
    assert not inspect(44)
    assert inspect(77.7)

    inspect = std.floats_nan_str(verb=INSP_JSON, typ=float, ctx=Rules())
    assert not inspect("string")
    assert not inspect("-inf")
    assert inspect(float("-inf"))
    assert inspect(44)
    assert inspect(77.7)


def test_floats_picklable():
    "Test that actions generated by the floats rule can be pickled."

    actions = [
        rule(verb=verb, typ=float, ctx=Rules())
        for verb in [JSON2PY, PY2JSON, INSP_PY, INSP_JSON]
        for rule in (std.floats, std.floats_nan_str)
    ]
    assert None not in actions
    dumps(actions)


def test_decimals_disregard():
    "Test the decimals rule will disregard unknown types and verbs."

    assert std.decimals(verb="unknown", typ=date, ctx=Rules()) is None
    assert std.decimals(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.decimals(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None
    assert std.decimals(verb=INSP_JSON, typ=Mystery, ctx=Rules()) is None
    assert std.decimals(verb=INSP_PY, typ=Mystery, ctx=Rules()) is None


def test_decimals():
    "Test the decimals rule will generate encoders and decoders for decimals."

    decoder = std.decimals(verb=JSON2PY, typ=Decimal, ctx=Rules())
    assert decoder(Decimal("77.7")) == Decimal("77.7")

    encoder = std.decimals(verb=PY2JSON, typ=Decimal, ctx=Rules())
    assert encoder(Decimal("77.7")) == Decimal("77.7")

    inspect = std.decimals(verb=INSP_PY, typ=Decimal, ctx=Rules())
    assert not inspect("string")
    assert not inspect(44)
    assert not inspect(77.7)
    assert not inspect("77.7")
    assert inspect(Decimal("77.7"))

    inspect = std.decimals(verb=INSP_JSON, typ=Decimal, ctx=Rules())
    assert not inspect("string")
    assert not inspect(44)
    assert not inspect(77.7)
    assert not inspect("77.7")
    assert inspect(Decimal("77.7"))


def test_decimals_as_str_disregard():
    "Test the decimals_as_str rule will disregard unknown types and verbs."

    assert std.decimals_as_str(verb="unknown", typ=date, ctx=Rules()) is None
    assert std.decimals_as_str(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.decimals_as_str(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None
    assert std.decimals_as_str(verb=INSP_JSON, typ=Mystery, ctx=Rules()) is None
    assert std.decimals_as_str(verb=INSP_PY, typ=Mystery, ctx=Rules()) is None


def test_decimals_as_str():
    "Test the decimals_as_str rule will generate encoders and decoders for decimals."

    decoder = std.decimals_as_str(verb=JSON2PY, typ=Decimal, ctx=Rules())
    assert decoder(Decimal("77.7")) == Decimal("77.7")
    assert decoder("77.7") == Decimal("77.7")

    encoder = std.decimals_as_str(verb=PY2JSON, typ=Decimal, ctx=Rules())
    assert encoder(Decimal("77.7")) == "77.7"

    inspect = std.decimals_as_str(verb=INSP_PY, typ=Decimal, ctx=Rules())
    assert not inspect("string")
    assert not inspect(44)
    assert not inspect(77.7)
    assert not inspect("77.7")
    assert inspect(Decimal("77.7"))

    inspect = std.decimals_as_str(verb=INSP_JSON, typ=Decimal, ctx=Rules())
    assert not inspect("string")
    assert inspect(44)
    assert inspect(77.7)
    assert inspect("77.7")
    assert inspect(Decimal("77.7"))


def test_iso_dates_disregard():
    "Test the iso_dates rule will disregard unknown types and verbs."

    assert std.iso_dates(verb="unknown", typ=date, ctx=Rules()) is None
    assert std.iso_dates(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.iso_dates(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None
    assert std.iso_dates(verb=INSP_JSON, typ=Mystery, ctx=Rules()) is None
    assert std.iso_dates(verb=INSP_PY, typ=Mystery, ctx=Rules()) is None


def test_iso_dates():
    "Test the iso_dates rule handles dates using ISO8601, rejecting datetimes as input to dates."

    decoder = std.iso_dates(verb=JSON2PY, typ=date, ctx=Rules())
    assert decoder("1776-07-04") == date(1776, 7, 4)
    with pytest.raises(ValueError):
        decoder("6543-02-01T09:09:09")

    encoder = std.iso_dates(verb=PY2JSON, typ=date, ctx=Rules())
    assert encoder(date(1776, 7, 4)) == "1776-07-04"

    inspect = std.iso_dates(verb=INSP_PY, typ=date, ctx=Rules())
    assert inspect(date(1776, 7, 4))
    assert not inspect(datetime(1776, 7, 4, 3, 3))
    assert not inspect("2000-01-01")
    assert not inspect("2000-01-01T03:03:03")
    assert not inspect("string")

    inspect = std.iso_dates(verb=INSP_JSON, typ=date, ctx=Rules())
    assert not inspect(date(1776, 7, 4))
    assert not inspect(datetime(1776, 7, 4, 3, 3))
    assert inspect("2000-01-01")
    assert not inspect("2000-01-01T03:03:03")
    assert not inspect("string")


def test_iso_datetimes():
    "Test the iso_dates rule will generate encoders and decoders for datetimes using ISO8601."

    decoder = std.iso_dates(verb=JSON2PY, typ=datetime, ctx=Rules())
    assert decoder("6666-06-06T12:12:12.987654") == datetime(
        6666, 6, 6, 12, 12, 12, 987654
    )

    encoder = std.iso_dates(verb=PY2JSON, typ=datetime, ctx=Rules())
    assert (
        encoder(datetime(6666, 6, 6, 12, 12, 12, 987654))
        == "6666-06-06T12:12:12.987654"
    )

    inspect = std.iso_dates(verb=INSP_PY, typ=datetime, ctx=Rules())
    assert not inspect(date(1776, 7, 4))
    assert inspect(datetime(1776, 7, 4, 3, 3))
    assert not inspect("2000-01-01")
    assert not inspect("2000-01-01T03:03:03")
    assert not inspect("string")

    inspect = std.iso_dates(verb=INSP_JSON, typ=datetime, ctx=Rules())
    assert not inspect(date(1776, 7, 4))
    assert not inspect(datetime(1776, 7, 4, 3, 3))
    assert inspect("2000-01-01")
    assert inspect("2000-01-01T03:03:03")
    assert not inspect("string")


def test_iso_dates_picklable():
    "Test that actions generated by the iso_dates rule can be pickled."

    actions = [
        std.iso_dates(verb=verb, typ=typ, ctx=Rules())
        for verb in [JSON2PY, PY2JSON]
        for typ in [date, datetime]
    ]
    assert None not in actions
    dumps(actions)


class Enum1(Enum):
    ABLE = "a"
    BAKER = "b"
    CHARLIE = "c"


class Enum2(IntEnum):
    ALPHA = 1
    BETA = 2
    GAMMA = 3


def test_enums_disregard():
    "Test the iso_dates rule will disregard unknown types and verbs."

    assert std.enums(verb="unknown", typ=Enum1, ctx=Rules()) is None
    assert std.enums(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.enums(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None


def test_enums():
    "Test the enums rule will generate encoders and decoders for enumerated types."

    decoder = std.enums(verb=JSON2PY, typ=Enum1, ctx=Rules())
    assert decoder("ABLE") == Enum1.ABLE
    assert decoder("CHARLIE") == Enum1.CHARLIE

    encoder = std.enums(verb=PY2JSON, typ=Enum1, ctx=Rules())
    assert encoder(Enum1.BAKER) == "BAKER"
    assert encoder(Enum1.CHARLIE) == "CHARLIE"

    inspect = std.enums(verb=INSP_PY, typ=Enum1, ctx=Rules())
    assert not inspect("ABLE")
    assert inspect(Enum1.CHARLIE)
    assert not inspect(Enum2.BETA)

    inspect = std.enums(verb=INSP_JSON, typ=Enum1, ctx=Rules())
    assert not inspect(Enum1.BAKER)
    assert not inspect("BETA")
    assert inspect("CHARLIE")


def test_enums_int():
    "Test the enums rule will generate encoders and decoders for enumerated type subclasses."
    decoder = std.enums(verb=JSON2PY, typ=Enum2, ctx=Rules())
    assert decoder("ALPHA") == Enum2.ALPHA
    assert decoder("GAMMA") == Enum2.GAMMA

    encoder = std.enums(verb=PY2JSON, typ=Enum2, ctx=Rules())
    assert encoder(Enum2.BETA) == "BETA"
    assert encoder(Enum2.GAMMA) == "GAMMA"

    inspect = std.enums(verb=INSP_PY, typ=Enum2, ctx=Rules())
    assert not inspect("ALPA")
    assert not inspect(Enum1.CHARLIE)
    assert inspect(Enum2.BETA)

    inspect = std.enums(verb=INSP_JSON, typ=Enum2, ctx=Rules())
    assert not inspect(Enum2.GAMMA)
    assert inspect("BETA")
    assert not inspect("ABLE")


def test_enums_picklable():
    "Test that actions generated by the enums rule can be pickled."

    actions = [
        std.enums(verb=verb, typ=typ, ctx=Rules())
        for verb in [JSON2PY, PY2JSON, INSP_PY, INSP_JSON]
        for typ in [Enum1, Enum2]
    ]
    assert None not in actions
    dumps(actions)


def test_faux_enums_disregard():
    "Test the iso_dates rule will disregard unknown types and verbs."

    assert std.faux_enums(verb="unknown", typ=Enum1, ctx=Rules()) is None
    assert std.faux_enums(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.faux_enums(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None


def test_faux_enums():
    "Test the enums rule will generate encoders and decoders for enumerated types."

    decoder = std.faux_enums(verb=JSON2PY, typ=Enum1, ctx=Rules())
    assert decoder("ABLE") == "ABLE"
    with pytest.raises(KeyError):
        decoder("OTHER")

    encoder = std.faux_enums(verb=PY2JSON, typ=Enum1, ctx=Rules())
    assert encoder("BAKER") == "BAKER"
    with pytest.raises(KeyError):
        encoder("OTHER")

    inspect = std.faux_enums(verb=INSP_PY, typ=Enum1, ctx=Rules())
    assert inspect("ABLE")
    assert not inspect(Enum1.CHARLIE)
    assert not inspect(Enum2.BETA)

    inspect = std.faux_enums(verb=INSP_JSON, typ=Enum1, ctx=Rules())
    assert not inspect(Enum1.BAKER)
    assert not inspect("BETA")
    assert inspect("CHARLIE")


def test_faux_enums_picklable():
    "Test that actions generated by the enums rule can be pickled."

    actions = [
        std.faux_enums(verb=verb, typ=typ, ctx=Rules())
        for verb in [JSON2PY, PY2JSON, INSP_PY, INSP_JSON]
        for typ in [Enum1, Enum2]
    ]
    assert None not in actions
    dumps(actions)


def test_optional_disregard():
    "Test that optional will disregard unknown types and verbs."

    assert std.optional(verb="unknown", typ=Optional[int], ctx=Rules()) is None
    assert std.optional(verb=JSON2PY, typ=Union[int, str], ctx=Rules()) is None
    assert (
        std.optional(verb=JSON2PY, typ=Union[int, str, NoneType], ctx=Rules()) is None
    )
    assert std.optional(verb=JSON2PY, typ=Mystery, ctx=Rules()) is None
    assert std.optional(verb=PY2JSON, typ=Mystery, ctx=Rules()) is None


def test_optional():
    "Test that optional returns a action that pass non-null values to an inner action."

    ctx = Rules(std.atoms)

    encoder = std.optional(verb=PY2JSON, typ=Optional[int], ctx=ctx)
    assert encoder("77") == 77
    assert encoder(None) is None

    decoder = std.optional(verb=JSON2PY, typ=Optional[int], ctx=ctx)
    assert decoder("77") == 77
    assert decoder(None) is None

    inspect = std.optional(verb=INSP_PY, typ=Optional[int], ctx=ctx)
    assert inspect(77)
    assert inspect(None)
    assert not inspect("77")

    inspect = std.optional(verb=INSP_JSON, typ=Optional[int], ctx=ctx)
    assert inspect(77)
    assert inspect(None)
    assert not inspect("77")


def test_optional_nonstandard():
    "Test that optional recognizes Unions that are effectively Optional."

    ctx = Rules(std.atoms)

    encoder = std.optional(verb=PY2JSON, typ=Union[str, NoneType], ctx=ctx)
    assert encoder(77) == "77"
    assert encoder(None) is None

    decoder = std.optional(verb=JSON2PY, typ=Union[str, NoneType], ctx=ctx)
    assert decoder(77) == "77"
    assert decoder(None) is None


def test_optional_invalid():
    "Test that optional raises if no valid inner type is found."

    ctx = Rules(std.atoms)
    fake_type = Mock(__origin__=Union, __args__=(NoneType, NoneType))

    for verb in (JSON2PY, PY2JSON, INSP_PY, INSP_JSON):
        with pytest.raises(TypeError):
            std.optional(verb=verb, typ=fake_type, ctx=ctx)


def test_optional_picklable():
    "Test that actions generated by the optional rule can be pickled."

    ctx = Rules(std.atoms, std.floats)

    actions = [
        std.optional(verb=verb, typ=typ, ctx=ctx)
        for verb in [JSON2PY, PY2JSON]
        for typ in [Optional[str], Optional[float], Optional[int], Optional[bool]]
    ]
    assert None not in actions
    dumps(actions)


def test_lists_disregards():
    "Test that lists disregards unknown types and verbs."

    assert std.lists(verb="unknown", typ=List[int], ctx=Rules()) is None
    assert std.lists(verb="unknown", typ=Tuple[int, ...], ctx=Rules()) is None
    assert std.lists(verb=PY2JSON, typ=bool, ctx=Rules()) is None
    assert std.lists(verb=JSON2PY, typ=Tuple[int, str], ctx=Rules()) is None
    assert std.lists(verb=INSP_PY, typ=bool, ctx=Rules()) is None
    assert std.lists(verb=INSP_JSON, typ=Tuple[int, str], ctx=Rules()) is None


def test_lists_lists():
    "Test that lists will generate encoders and decoders for lists."

    ctx = Rules(std.atoms)

    encoder = std.lists(verb=PY2JSON, typ=List[str], ctx=ctx)
    assert encoder([33, 77]) == ["33", "77"]

    decoder = std.lists(verb=JSON2PY, typ=List[str], ctx=ctx)
    assert decoder([33, 77]) == ["33", "77"]

    inspect = std.lists(verb=INSP_PY, typ=List[str], ctx=ctx)
    assert not inspect(["33", 77])
    assert inspect(["33", "77"])
    assert not inspect(("33", "77"))

    inspect = std.lists(verb=INSP_JSON, typ=List[str], ctx=ctx)
    assert not inspect(["33", 77])
    assert inspect(["33", "77"])
    assert not inspect(("33", "77"))


def test_lists_tuples():
    "Test that lists will generate encoders and decoders for homogenous tuples."

    ctx = Rules(std.atoms)

    encoder = std.lists(verb=PY2JSON, typ=Tuple[str, ...], ctx=ctx)
    assert encoder((33, 77)) == ["33", "77"]

    decoder = std.lists(verb=JSON2PY, typ=Tuple[str, ...], ctx=ctx)
    assert decoder([33, 77]) == ("33", "77")

    inspect = std.lists(verb=INSP_PY, typ=Tuple[str, ...], ctx=ctx)
    assert not inspect(("33", 77))
    assert inspect(("33", "77"))
    assert not inspect(["33", "77"])

    inspect = std.lists(verb=INSP_JSON, typ=Tuple[str, ...], ctx=ctx)
    assert not inspect(["33", 77])
    assert inspect(["33", "77"])
    assert not inspect(("33", "77"))

    # Prove these tests don't pass spuriously.
    assert ["1", "2"] != ("1", "2")


def test_sets_disregards():
    "Test that sets disregards unknown types and verbs."

    assert std.sets(verb="unknown", typ=Set[int], ctx=Rules()) is None
    assert std.sets(verb="unknown", typ=FrozenSet[set], ctx=Rules()) is None
    assert std.sets(verb=PY2JSON, typ=bool, ctx=Rules()) is None
    assert std.sets(verb=JSON2PY, typ=List[str], ctx=Rules()) is None
    assert std.sets(verb=INSP_PY, typ=bool, ctx=Rules()) is None
    assert std.sets(verb=INSP_JSON, typ=List[str], ctx=Rules()) is None


def test_sets_sets():
    "Test that sets will generate encoders and decoders for sets."

    ctx = Rules(std.atoms)

    encoder = std.sets(verb=PY2JSON, typ=Set[str], ctx=ctx)
    actual = encoder({1, 2, 2, 3})
    actual.sort()
    assert actual == ["1", "2", "3"]

    decoder = std.sets(verb=JSON2PY, typ=Set[str], ctx=ctx)
    assert decoder([1, 2, 2, 3]) == {"1", "2", "3"}

    inspect = std.sets(verb=INSP_PY, typ=Set[str], ctx=ctx)
    assert not inspect({"33", 77})
    assert inspect({"33", "77"})
    assert not inspect(["33", "77"])

    inspect = std.sets(verb=INSP_JSON, typ=Set[str], ctx=ctx)
    assert not inspect(["33", 77])
    assert inspect(["33", "77"])
    assert not inspect({"33", "77"})


def test_sets_frozen():
    "Test that sets will generate encoders and decoders for frozen sets."

    ctx = Rules(std.atoms)

    encoder = std.sets(verb=PY2JSON, typ=FrozenSet[str], ctx=ctx)
    actual = encoder(frozenset([1, 2, 2, 3]))
    actual.sort()
    assert actual == ["1", "2", "3"]

    decoder = std.sets(verb=JSON2PY, typ=FrozenSet[str], ctx=ctx)
    assert decoder([1, 2, 2, 3]) == frozenset(["1", "2", "3"])

    inspect = std.sets(verb=INSP_PY, typ=FrozenSet[str], ctx=ctx)
    assert not inspect(frozenset({"33", 77}))
    assert inspect(frozenset({"33", "77"}))
    assert not inspect(["33", "77"])

    inspect = std.sets(verb=INSP_JSON, typ=FrozenSet[str], ctx=ctx)
    assert not inspect(["33", 77])
    assert inspect(["33", "77"])
    assert not inspect({"33", "77"})


def test_dicts_disregards():
    "Test that dicts disregards unknown types and verbs."

    ctx = Rules(stringify_keys, std.atoms, std.floats)

    assert std.dicts(verb="unknown", typ=Dict[str, int], ctx=ctx) is None
    assert std.dicts(verb="unknown", typ=Dict[datetime, float], ctx=ctx) is None
    if OrderedDict is not None:
        assert std.dicts(verb="unknown", typ=OrderedDict[str, int], ctx=ctx) is None
        assert (
            std.dicts(verb="unknown", typ=OrderedDict[datetime, float], ctx=ctx) is None
        )
    assert std.dicts(verb=PY2JSON, typ=bool, ctx=ctx) is None
    with pytest.raises(RuntimeError):
        std.dicts(verb=JSON2PY, typ=Dict[float, str], ctx=ctx)

    assert std.dicts(verb=INSP_JSON, typ=List[str], ctx=ctx) is None


def test_dicts_string_key():
    "Test that dicts will generate encoders and decoders for dicts."

    ctx = Rules(stringify_keys, std.atoms)

    encoder = std.dicts(verb=PY2JSON, typ=Dict[str, int], ctx=ctx)
    assert encoder({22: "11", 44: "33"}) == {"22": 11, "44": 33}

    decoder = std.dicts(verb=JSON2PY, typ=Dict[str, int], ctx=ctx)
    assert decoder({22: "11", 44: "33"}) == {"22": 11, "44": 33}

    inspect = std.dicts(verb=INSP_PY, typ=Dict[str, int], ctx=ctx)
    assert not inspect({"foo": 1, "bar": "no"})
    assert inspect({"foo": 1, "bar": 2})
    assert inspect({})

    inspect = std.dicts(verb=INSP_JSON, typ=Dict[str, int], ctx=ctx)
    assert not inspect({"foo": 1, "bar": "no"})
    assert inspect({"foo": 1, "bar": 2})
    assert inspect({})


def test_dicts_date_key():
    "Test that dicts will generate encoders and decoders for dicts with simple dates as keys."

    ctx = Rules(std.atoms, std.iso_dates, stringify_keys)

    encoder = std.dicts(verb=PY2JSON, typ=Dict[date, int], ctx=ctx)
    assert encoder({date(2020, 2, 22): "11", date(2040, 4, 4): "33"}) == {
        "2020-02-22": 11,
        "2040-04-04": 33,
    }

    decoder = std.dicts(verb=JSON2PY, typ=Dict[date, int], ctx=ctx)
    assert decoder({"2020-02-22": "11", "2040-04-04": "33"}) == {
        date(2020, 2, 22): 11,
        date(2040, 4, 4): 33,
    }

    inspect = std.dicts(verb=INSP_PY, typ=Dict[date, int], ctx=ctx)
    assert not inspect({date(2040, 4, 4): 1, date(2020, 2, 22): "no"})
    assert inspect({date(2040, 4, 4): 1, date(2020, 2, 22): 2})
    assert inspect({})

    inspect = std.dicts(verb=INSP_JSON, typ=Dict[date, int], ctx=ctx)
    assert not inspect({"2011-11-11": 1, "2022-02-02": "no"})
    assert inspect({"2011-11-11": 1, "2022-02-02": 2})
    assert inspect({})


class AB(Enum):
    A = 1
    B = 2


def test_dicts_enum_key():
    "Test that dicts will generate encoders and decoders for dicts."

    ctx = Rules(stringify_keys, std.atoms, std.enums)

    encoder = std.dicts(verb=PY2JSON, typ=Dict[AB, int], ctx=ctx)
    assert encoder({AB.A: "11", AB.B: "33"}) == {"A": 11, "B": 33}

    decoder = std.dicts(verb=JSON2PY, typ=Dict[AB, int], ctx=ctx)
    assert decoder({"A": "11", "B": "33"}) == {AB.A: 11, AB.B: 33}

    inspect = std.dicts(verb=INSP_PY, typ=Dict[AB, int], ctx=ctx)
    assert not inspect({AB.A: 1, AB.B: "no"})
    assert inspect({AB.A: 1, AB.B: 2})
    assert not inspect({AB.A: 1, "B": 2})

    inspect = std.dicts(verb=INSP_JSON, typ=Dict[AB, int], ctx=ctx)
    assert not inspect({"A": 1, "B": "no"})
    assert inspect({"A": 1, "B": 2})
    assert not inspect({"A": 1, "C": 2})
