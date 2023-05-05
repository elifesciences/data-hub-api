from typing import Mapping, Optional, Sequence, TypedDict
from typing_extensions import NotRequired


DocmapOutput = TypedDict(
    'DocmapOutput',
    {
        'type': str,
        'doi': Optional[str],
        'published': NotRequired[str],
        'license': NotRequired[str],
        'url': NotRequired[Optional[str]],
        'versionIdentifier': NotRequired[str],
        'identifier': NotRequired[str],
        '_tdmPath': NotRequired[str],
        'content': NotRequired[Sequence[dict]]
    },
    total=False
)

DocmapParticipant = TypedDict(
    'DocmapParticipant',
    {
        'actor': dict,
        'role': str
    },
    total=False
)

DocmapInput = TypedDict(
    'DocmapInput',
    {
        'type': str,
        'doi': str,
        'url': NotRequired[str],
        'versionIdentifier': NotRequired[str]
    },
    total=False
)

DocmapAssertion = TypedDict(
    'DocmapAssertion',
    {
        'item': dict,
        'status': str,
        'happened': NotRequired[str]
    },
    total=False
)

DocmapAction = TypedDict(
    'DocmapAction',
    {
        'participants': Sequence[DocmapParticipant],
        'outputs': Sequence[DocmapOutput]
    }
)

DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[DocmapAction],
        'assertions': Sequence[DocmapAssertion],
        'inputs': Sequence[DocmapInput],
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
