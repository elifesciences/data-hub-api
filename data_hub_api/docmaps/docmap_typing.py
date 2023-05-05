from typing import Mapping, TypedDict


DocmapSteps = Mapping[str, dict]

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
