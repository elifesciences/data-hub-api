from typing import Mapping, Sequence, TypedDict
from typing_extensions import NotRequired


DocmapParticipants = TypedDict(
    'DocmapParticipants',
    {
        'actor': dict,
        'role': str
    },
    total=False
)

DocmapInputs = TypedDict(
    'DocmapInputs',
    {
        'type': str,
        'doi': str,
        'url': NotRequired[str],
        'versionIdentifier': NotRequired[str]
    },
    total=False
)

DocmapAssertions = TypedDict(
    'DocmapAssertions',
    {
        'item': dict,
        'status': str,
        'happened': NotRequired[str]
    },
    total=False
)

DocmapActions = TypedDict(
    'DocmapActions',
    {
        'participants': Sequence[DocmapParticipants],
        'outputs': Sequence[dict]
    }
)

DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[DocmapActions],
        'assertions': Sequence[DocmapAssertions],
        'inputs': Sequence[DocmapInputs],
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
