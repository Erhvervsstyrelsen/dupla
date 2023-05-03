import pytest
from datetime import date, datetime
from dupla import validation

# Constant dates, ensures they do not change during test
TODAY = date.today()
TODAY_DT = datetime.now()


@pytest.mark.parametrize(
    "date_inp,is_valid",
    [
        ("2012-12-12", True),
        ("2012-13-12", False),
        ("03-05-2020", False),
        ("01-01-20", False),
    ],
)
def test_validate_iso(date_inp, is_valid):
    assert validation.validate_iso_date(date_inp) == is_valid


@pytest.mark.parametrize(
    "date_inp,expected",
    [
        (datetime.strptime("12-03-2020", "%d-%m-%Y"), "2020-03-12"),
        (TODAY_DT, TODAY_DT.strftime("%Y-%m-%d")),
        (TODAY, TODAY.strftime("%Y-%m-%d")),
    ],
)
def test_convert_and_validate_iso(date_inp, expected):
    output = validation.convert_and_validate_iso_date(date_inp)
    assert isinstance(output, str)
    assert output == expected


@pytest.mark.parametrize("date_inp", ["03-05-2020", "2017-13-01"])
def test_invalid_iso(date_inp):
    with pytest.raises(ValueError):
        validation.convert_and_validate_iso_date(date_inp)
