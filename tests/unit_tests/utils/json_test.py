from datetime import date, datetime
import json

import numpy as np

from data_hub_api.utils.json import (
    get_json_compatible_value,
    get_recursive_json_compatible_value,
    get_recursively_transformed_object,
    parse_json_if_string_or_return_value,
    remove_key_with_none_value_only,
    is_none_value
)


# reformatting to avoid issues with changes to formatting
DATETIME_STR_1 = datetime.fromisoformat('2021-02-03T04:05:06+00:00').isoformat()

DATE_STR_1 = date.fromisoformat('2021-02-03').isoformat()


class TestIsNoneValue:
    def test_should_return_true_for_a_none_value(self):
        assert is_none_value(None)

    def test_should_return_false_for_a_non_empty_string(self):
        assert not is_none_value('string')

    def test_should_return_false_for_an_empty_string(self):
        assert not is_none_value('')

    def test_should_return_false_for_a_number(self):
        assert not is_none_value(123)

    def test_should_return_false_for_a_non_empty_list(self):
        assert not is_none_value([1, 2, 3])

    def test_should_return_false_for_an_empty_list(self):
        assert not is_none_value([])

    def test_should_return_false_for_a_non_empty_dict(self):
        assert not is_none_value({'key': 1})

    def test_should_return_false_for_an_empty_dict(self):
        assert not is_none_value({})

    def test_shoul_return_false_for_a_list_with_value_number_zero(self):
        assert not is_none_value([0])

    def test_should_return_false_for_a_number_zero(self):
        assert not is_none_value(0)

    def test_should_return_false_for_a_float_zero(self):
        assert not is_none_value(0.0)


class TestGetJsonCompatibleValue:
    def test_should_not_change_str(self):
        assert get_json_compatible_value('test123') == 'test123'

    def test_should_format_datetime(self):
        assert get_json_compatible_value(datetime.fromisoformat(DATETIME_STR_1)) == DATETIME_STR_1

    def test_should_format_date(self):
        assert get_json_compatible_value(date.fromisoformat(DATE_STR_1)) == DATE_STR_1


class TestGetRecursiveJsonCompatibleValue:
    def test_should_format_datetime_within_a_dict(self):
        assert get_recursive_json_compatible_value(
            {'key': datetime.fromisoformat(DATETIME_STR_1)}
        ) == {'key': DATETIME_STR_1}

    def test_should_format_datetime_within_a_list(self):
        assert get_recursive_json_compatible_value(
            [datetime.fromisoformat(DATETIME_STR_1)]
        ) == [DATETIME_STR_1]


class TestGetRecursivelyTransformedObject:
    def test_should_transform_dict_value(self):
        assert get_recursively_transformed_object(
            {'key1': 'old value1'},
            key_value_transform_fn=lambda key, value: (
                (key, 'new value1')
            )
        ) == {'key1': 'new value1'}

    def test_should_transform_dict_key_and_value(self):
        assert get_recursively_transformed_object(
            {'old_key1': 'old value1'},
            key_value_transform_fn=lambda key, value: (
                ('new_key1', 'new value1')
            )
        ) == {'new_key1': 'new value1'}

    def test_should_delete_item_if_transformed_key_is_none(self):
        assert get_recursively_transformed_object(
            {'old_key1': 'old value1'},
            key_value_transform_fn=lambda key, value: (
                (None, 'new value1')
            )
        ) == {}

    def test_should_transform_dict_value_inside_another_dict(self):
        assert get_recursively_transformed_object(
            {'parent': {'key1': 'old value1'}},
            key_value_transform_fn=lambda key, value: (
                (key, 'new value1' if key == 'key1' else value)
            )
        ) == {'parent': {'key1': 'new value1'}}

    def test_should_transform_dict_value_inside_a_list(self):
        assert get_recursively_transformed_object(
            [{'key1': 'old value1'}],
            key_value_transform_fn=lambda key, value: (
                (key, 'new value1' if key == 'key1' else value)
            )
        ) == [{'key1': 'new value1'}]


class TestRemoveKeyWithNoneValueOnly:
    def test_should_remove_none_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': None,
            'other': 'value'
        }) == {'other': 'value'}

    def test_should_remove_none_from_list(self):
        assert remove_key_with_none_value_only([
            'item1', None
        ]) == ['item1']

    def test_should_remove_empty_string_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': '',
            'other': 'value'
        }) == {'key1': '', 'other': 'value'}

    def test_should_remove_empty_string_from_list(self):
        assert remove_key_with_none_value_only([
            'item1', ''
        ]) == ['item1', '']

    def test_should_remove_empty_list_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': [],
            'other': 'value'
        }) == {'key1': [], 'other': 'value'}

    def test_should_return_list_without_none_value_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': ['item1', None],
            'other': 'value'
        }) == {'key1': ['item1'], 'other': 'value'}

    def test_should_return_list_without_empty_string_value_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': ['item1', ''],
            'other': 'value'
        }) == {'key1': ['item1', ''], 'other': 'value'}

    def test_should_remove_not_remove_false_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': False,
            'other': 'value'
        }) == {'key1': False, 'other': 'value'}

    def test_should_remove_np_nan_from_dict(self):
        assert remove_key_with_none_value_only({
            'key1': np.nan,
            'other': 'value'
        }) == {'other': 'value'}

    def test_should_not_fail_with_np_array(self):
        record = {
            'key1': np.asarray([1, 2, 3]),
            'other': 'value'
        }
        assert remove_key_with_none_value_only(record.copy()) == record

    def test_should_remove_none_from_dict_within_list(self):
        assert remove_key_with_none_value_only([{
            'key1': None,
            'other': 'value'
        }]) == [{'other': 'value'}]

    def test_should_remove_none_from_dict_within_dict(self):
        assert remove_key_with_none_value_only({
            'parent': {
                'key1': None,
                'other': 'value'
            }
        }) == {
            'parent': {'other': 'value'}
        }

    def test_should_not_modify_passed_in_value(self):
        record = {
            'key1': None,
            'other': 'value'
        }
        record_copy = record.copy()
        remove_key_with_none_value_only(record)
        assert record == record_copy


class TestParseJsonIfStringOrReturnValue:
    def test_should_return_passed_in_dict_as_is(self):
        assert parse_json_if_string_or_return_value({'name': 'test'}) == {'name': 'test'}

    def test_should_parse_json(self):
        assert parse_json_if_string_or_return_value(
            json.dumps({'name': 'test'})
        ) == {'name': 'test'}
