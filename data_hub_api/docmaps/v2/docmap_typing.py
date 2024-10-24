from typing import Mapping, Optional, Sequence, TypedDict, Union
from typing_extensions import NotRequired

date_str = str
timestamp_str = str

DocmapContent = TypedDict(
    'DocmapContent',
    {
        'type': str,
        'url': str
    }
)

DocmapEvaluationOutput = TypedDict(
    'DocmapEvaluationOutput',
    {
        'type': str,
        'doi': Optional[str],
        'published': timestamp_str,
        'license': str,
        'url': Optional[str],
        'content': Sequence[DocmapContent]
    }
)

DocmapElifeManuscriptInput = TypedDict(
    'DocmapElifeManuscriptInput',
    {
        'type': str,
        'doi': str,
        'identifier': str,
        'versionIdentifier': str
    }
)

DocmapElifeManuscriptOutput = TypedDict(
    'DocmapElifeManuscriptOutput',
    {
        'type': str,
        'doi': str,
        'identifier': str,
        'versionIdentifier': str,
        'license': str
    }
)

DocmapPartOfComplement = TypedDict(
    'DocmapPartOfComplement',
    {
        'type': str,
        'url': str,
        'title': Optional[str],
        'description': Optional[str],
        'thumbnail': Optional[str]
    },
    total=False
)

DocmapPublishedElifeManuscriptPartOf = TypedDict(
    'DocmapPublishedElifeManuscriptPartOf',
    {
        'type': str,
        'doi': str,
        'identifier': str,
        'subjectDisciplines': Optional[Sequence[str]],
        'published': timestamp_str,
        'volumeIdentifier': Optional[str],
        'electronicArticleIdentifier': str,
        'complement': Optional[Sequence[Optional[DocmapPartOfComplement]]]
    }
)

DocmapPublishedElifeManuscriptOutput = TypedDict(
    'DocmapPublishedElifeManuscriptOutput',
    {
        'type': str,
        'published': timestamp_str,
        'doi': str,
        'identifier': str,
        'versionIdentifier': str,
        'license': str,
        'partOf': DocmapPublishedElifeManuscriptPartOf
    }
)


DocmapElifeManuscriptVorOutput = TypedDict(
    'DocmapElifeManuscriptVorOutput',
    {
        'type': str,
        'identifier': str,
        'doi': str,
        'versionIdentifier': str,
        'published': Optional[date_str],
        'url': str,
        'content': Sequence[DocmapContent]
    }
)

DocmapAnonymousActor = TypedDict(
    'DocmapAnonymousActor',
    {
        'type': str,
        'name': str
    }
)

DocmapAffiliation = TypedDict(
    'DocmapAffiliation',
    {
        'type': str,
        'name': str,
        'location': Optional[str]
    }
)

DocmapEditorActor = TypedDict(
    'DocmapEditorActor',
    {
        'type': str,
        'name': str,
        'firstName': str,
        '_middleName': Optional[str],
        'surname': str,
        '_relatesToOrganization': str,
        'affiliation': Optional[DocmapAffiliation]
    }
)

DocmapParticipant = TypedDict(
    'DocmapParticipant',
    {
        'actor': Union[DocmapEditorActor, DocmapAnonymousActor],
        'role': str
    },
    total=False
)

DocmapPreprintInput = TypedDict(
    'DocmapPreprintInput',
    {
        'type': str,
        'doi': str,
        'url': Optional[str],
        'versionIdentifier': Optional[str]
    }
)

DocmapPreprintInputWithPublishedMecaPath = TypedDict(
    'DocmapPreprintInputWithPublishedMecaPath',
    {
        'type': str,
        'doi': str,
        'url': str,
        'versionIdentifier': str,
        'published': Optional[timestamp_str],
        'content': Optional[Sequence[DocmapContent]]
    },
    total=False
)

DocmapEvaluationInput = TypedDict(
    'DocmapEvaluationInput',
    {
        'type': str,
        'doi': Optional[str]
    }
)

DocmapAssertionItem = TypedDict(
    'DocmapAssertionItem',
    {
        'type': str,
        'doi': Optional[str],
        'versionIdentifier': Optional[str]
    }
)

DocmapAssertion = TypedDict(
    'DocmapAssertion',
    {
        'item': DocmapAssertionItem,
        'status': str,
        'happened': NotRequired[Optional[str]]
    },
    total=False
)

DocmapAction = TypedDict(
    'DocmapAction',
    {
        'participants': Sequence[DocmapParticipant],
        'outputs': Sequence[
            Union[
                DocmapElifeManuscriptOutput,
                DocmapEvaluationOutput,
                DocmapElifeManuscriptVorOutput
            ]
        ]
    }
)

DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[DocmapAction],
        'assertions': Sequence[DocmapAssertion],
        'inputs': Sequence[Union[
            DocmapPreprintInput,
            DocmapEvaluationInput,
            DocmapElifeManuscriptInput
        ]],
        'next-step': NotRequired[str],
        'previous-step': NotRequired[str]
    },
    total=False
)

DocmapSteps = Mapping[str, DocmapStep]

Docmap = TypedDict(
    'Docmap',
    {
        '@context': str,
        'type': str,
        'id': str,
        'created': timestamp_str,
        'updated': timestamp_str,
        'publisher': dict,
        'first-step': str,
        'steps': DocmapSteps
    },
    total=False
)
