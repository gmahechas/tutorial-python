from LargeValueException import LargeValueException,  SmallValueException

try:
    value = 60
    if value < 20:
        raise SmallValueException("value is too small")

    if value > 50:
        raise LargeValueException("value is too large")

    print(value)

except SmallValueException as small:
    print(small)
except LargeValueException as large:
    print(large)
