from typing import Mapping, Sequence, TypedDict
from typing_extensions import NotRequired


DocmapInputs = TypedDict(
    'DocmapInputs',
    {
        'type': str,
        'doi': str,
        'url': str,
        'versionIdentifier': str
    },
    total=False
)

DocmapAssertions = TypedDict(
    'DocmapAssertions',
    {
        'item': dict,
        'status': str,
        'happened': str
    },
    total=False
)

DocmapActions = TypedDict(
    'DocmapActions',
    {
        'participants': Sequence[dict],
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
