from typing import Mapping, Optional, Sequence, TypedDict, Union
from typing_extensions import NotRequired


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
        'published': str,
        'license': str,
        'url': Optional[str],
        'content': Sequence[DocmapContent]
    }
)

DocmapElifeManuscriptOutput = TypedDict(
    'DocmapElifeManuscriptOutput',
    {
        'type': str,
        'doi': Optional[str],
        'identifier': str,
        'versionIdentifier': str,
        'license': str
    }
)

DocmapPreprintOutput = TypedDict(
    'DocmapPreprintOutput',
    {
        'type': str,
        'doi': Optional[str],
        'published': str,
        'url': Optional[str],
        'versionIdentifier': str,
        '_tdmPath': str
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
        'url': str,
        'versionIdentifier': str
    }
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
        'versionIdentifier': str
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
            Union[DocmapPreprintOutput, DocmapElifeManuscriptOutput, DocmapEvaluationOutput]
        ]
    }
)

DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[DocmapAction],
        'assertions': Sequence[DocmapAssertion],
        'inputs': Sequence[Union[DocmapPreprintInput, DocmapEvaluationInput]],
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
        'created': str,
        'updated': str,
        'publisher': dict,
        'first-step': str,
        'steps': DocmapSteps
    },
    total=False
)
