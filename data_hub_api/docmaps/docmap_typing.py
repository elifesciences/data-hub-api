from typing import Mapping, Sequence, TypedDict
from typing_extensions import NotRequired


DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[dict],
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
