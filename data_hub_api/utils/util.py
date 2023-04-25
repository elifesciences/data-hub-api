from typing import Any, List


def get_previous_element_of_given_element_in_given_list(
    given_list: List[Any],
    given_element: Any
) -> Any:
    for index, element in enumerate(given_list):
        if index != 0 and element == given_element:
            return given_list[index-1]
        continue
    return None
