import pytest

from data_hub_api.docmaps.v2.codecs.docmaps_steps import (
    generate_docmap_steps
)


class TestGenerateDocmapSteps:
    def test_should_return_empty_dict_if_step_list_empty(self):
        step_list = []
        steps = generate_docmap_steps(step_list)
        assert steps == {}

    def test_should_return_all_step_keys_for_each_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
        step_key_list = list(steps.keys())
        assert step_key_list == ['_:b0', '_:b1', '_:b2']

    def test_should_not_have_next_or_previous_step_keys_when_there_is_only_one_step(self):
        step_list = [{'step_1': 1}]
        steps = generate_docmap_steps(step_list)
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']
        with pytest.raises(KeyError):
            assert steps['_:b0']['next-step']

    def test_should_only_have_next_step_for_first_step_while_there_are_more_than_one_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}]
        steps = generate_docmap_steps(step_list)
        assert steps['_:b0']['next-step'] == '_:b1'
        with pytest.raises(KeyError):
            assert steps['_:b0']['previous-step']

    def test_should_have_both_next_and_previous_steps_keys_for_a_middle_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
        assert steps['_:b1']['next-step'] == '_:b2'
        assert steps['_:b1']['previous-step'] == '_:b0'

    def test_should_only_have_previous_step_for_latest_step(self):
        step_list = [{'step_1': 1}, {'step_2': 2}, {'step_3': 3}]
        steps = generate_docmap_steps(step_list)
        assert steps['_:b2']['previous-step'] == '_:b1'
        with pytest.raises(KeyError):
            assert steps['_:b2']['next-step']
