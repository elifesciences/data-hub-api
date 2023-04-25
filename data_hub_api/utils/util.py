from typing import Sequence, TypeVar


T = TypeVar('T')


def get_previous_element_of_given_element_in_given_list(
    given_list: Sequence[T],
    given_element: T
) -> T:
    for index, element in enumerate(given_list):
        if index != 0 and element == given_element:
            return given_list[index-1]
        continue
    raise KeyError('previous element not found')
