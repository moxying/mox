from enum import Enum
from core.utils.unionenum import enum_union, extend_enum


class BeforeDay(Enum):
    BEFORE = "Before"


class Weekday(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class AfterDay(Enum):
    AFTER = "After"


Day = enum_union(BeforeDay, Weekday, AfterDay)


print(list(Day))
print(len(Day))
print(Day.AFTER)
print(Day.AFTER.value)
print(list(Day).index(Day.BEFORE))
print(list(Day).index(Day.TUESDAY))
print(list(Day).index(Day.AFTER))
print(list(Day).index(Weekday.TUESDAY))


@extend_enum(Weekday)
class ExtendDay(Enum):
    AFTER = "After"


print(list(ExtendDay))
print(len(ExtendDay))
print(ExtendDay.AFTER)
print(ExtendDay.AFTER.value)
print(list(ExtendDay).index(ExtendDay.WEDNESDAY))
print(list(ExtendDay).index(ExtendDay.AFTER))
