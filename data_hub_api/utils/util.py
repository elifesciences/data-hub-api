def get_previous_element_of_given_element_in_list(given_list, given_element):
    for index, element in enumerate(given_list):
        if index != 0 and element == given_element:
            return given_list[index-1]
