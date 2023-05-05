from typing import Mapping, Sequence, TypedDict
from typing_extensions import NotRequired


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
        'assertions': Sequence[dict],
        'inputs': Sequence[dict],
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
