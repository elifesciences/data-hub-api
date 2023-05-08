from data_hub_api.docmaps.codecs.evaluation import get_elife_evaluation_doi


class TestGetElifeEvaluationDoi:
    def test_should_return_evaluation_doi_with_suffix_if_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = 'evaluation_suffix_1'
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1.evaluation_suffix_1'

    def test_should_return_evaluation_doi_without_suffix_if_not_defined(self):
        elife_doi = 'elife_doi_1'
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = ''
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert actual_result == 'elife_doi_1.elife_doi_version_str_1'

    def test_should_return_none_if_elife_doi_not_defined(self):
        elife_doi = ''
        elife_doi_version_str = 'elife_doi_version_str_1'
        evaluation_suffix = ''
        actual_result = get_elife_evaluation_doi(
            elife_doi=elife_doi,
            elife_doi_version_str=elife_doi_version_str,
            evaluation_suffix=evaluation_suffix
        )
        assert not actual_result
