from typing import Mapping, Optional, Sequence, TypedDict
from typing_extensions import NotRequired


DocmapOutputs = TypedDict(
    'DocmapOutputs',
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
        'outputs': Sequence[DocmapOutputs]
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
