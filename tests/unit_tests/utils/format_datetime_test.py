from data_hub_api.utils.format_datetime import format_datetime_with_utc_offset


class TestFormatDatetimeWithUtcOffset:
    def test_should_return_datetime_string_with_timestamp(self):
        result = format_datetime_with_utc_offset(
            date_string='2023-04-11 14:00:00'
        )
        assert result == '2023-04-11T14:00:00+00:00'

    def test_should_return_date_string_with_timestamp(self):
        result = format_datetime_with_utc_offset(
            date_string='2023-04-11'
        )
        assert result == '2023-04-11T00:00:00+00:00'

    def test_should_return_timestamp_as_it_is(self):
        result = format_datetime_with_utc_offset(
            date_string='2023-05-05T01:02:03+00:00'
        )
        assert result == '2023-05-05T01:02:03+00:00'

    def test_should_return_none_when_the_datetime_string_is_none(self):
        result = format_datetime_with_utc_offset(
            date_string=None
        )
        assert not result
