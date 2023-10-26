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
        'content': Sequence[DocmapContent]
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

DocmapAnonymousActor = TypedDict(
    'DocmapAnonymousActor',
    {
        'type': str,
        'name': str
    }
)

DocmapAffiliation = TypedDict(
    'DocmapAffiliation',
    {
        'type': str,
        'name': str,
        'location': Optional[str]
    }
)

DocmapEditorActor = TypedDict(
    'DocmapEditorActor',
    {
        'type': str,
        'name': str,
        'firstName': str,
        '_middleName': Optional[str],
        'surname': str,
        '_relatesToOrganization': str,
        'affiliation': DocmapAffiliation
    }
)

DocmapParticipant = TypedDict(
    'DocmapParticipant',
    {
        'actor': Union[DocmapEditorActor, DocmapAnonymousActor],
        'role': str
    },
    total=False
)

DocmapPreprintInput = TypedDict(
    'DocmapPreprintInput',
    {
        'type': str,
        'doi': str
    }
)

DocmapPreprintInputWithPublishedMecaPath = TypedDict(
    'DocmapPreprintInputWithPublishedMecaPath',
    {
        'type': str,
        'doi': str,
        'url': str,
        'versionIdentifier': str,
        'published': timestamp_str
    },
    total=False
)

DocmapAssertionItem = TypedDict(
    'DocmapAssertionItem',
    {
        'type': str,
        'doi': Optional[str]
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
                DocmapEvaluationOutput
            ]
        ]
    }
)

DocmapStep = TypedDict(
    'DocmapStep',
    {
        'actions': Sequence[DocmapAction],
        'assertions': Sequence[DocmapAssertion],
        'inputs': Sequence[DocmapPreprintInput],
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
