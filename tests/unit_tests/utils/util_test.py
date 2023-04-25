import pytest
from data_hub_api.utils.util import get_previous_element_of_given_element_in_given_list


class TestGetPreviousElementOfGivenElementInGivenList:
    def test_should_raise_keyerror_if_given_element_is_first_element_of_the_list(self):
        given_list = ['item_1', 'item_2']
        with pytest.raises(KeyError):
            get_previous_element_of_given_element_in_given_list(given_list, 'item_1')

    def test_should_raise_keyerror_if_given_element_is_not_in_the_list(self):
        given_list = ['item_1', 'item_2']
        with pytest.raises(KeyError):
            get_previous_element_of_given_element_in_given_list(given_list, 'item_3')

    def test_should_return_previous_element_of_given_element_in_the_list(self):
        given_list = ['item_1', 'item_2']
        actual_return = get_previous_element_of_given_element_in_given_list(given_list, 'item_2')
        assert actual_return == 'item_1'
