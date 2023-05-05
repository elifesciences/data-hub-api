from typing import TypedDict


DocmapTypedDict = TypedDict(
    'DocmapTypedDict',
    {
        '@context': str,
        'type': str,
        'id': str,
        'created': str,
        'updated': str,
        'publisher': dict,
        'first-step': str,
        'steps': dict
    },
    total=False
)
