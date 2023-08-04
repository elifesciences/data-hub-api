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
        'published': Optional[timestamp_str],
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

DocmapPublishedElifeManuscriptPartOf = TypedDict(
    'DocmapPublishedElifeManuscriptPartOf',
    {
        'type': str,
        'doi': str,
        'identifier': str,
        'volumeIdentifier': str,
        'electronicArticleIdentifier': str
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
        'doi': str,
        'published': Optional[date_str],
        'url': str,
        'content': Sequence[DocmapContent]
    }
)

DocmapParticipant = TypedDict(
    'DocmapParticipant',
    {
        'actor': dict,
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
        'published': timestamp_str,
        'content': Sequence[DocmapContent]
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
        'happened': NotRequired[str]
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
