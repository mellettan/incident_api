import pytest

from incident_api.models import ALLOWED_TRANSITIONS, Incident, IncidentStatus

S = IncidentStatus


@pytest.mark.parametrize(
    ("current", "target", "allowed"),
    [
        (S.NEW, S.IN_PROGRESS, True),
        (S.NEW, S.RESOLVED, True),
        (S.NEW, S.CLOSED, True),
        (S.IN_PROGRESS, S.NEW, False),
        (S.IN_PROGRESS, S.RESOLVED, True),
        (S.RESOLVED, S.IN_PROGRESS, True),
        (S.RESOLVED, S.NEW, False),
        (S.CLOSED, S.IN_PROGRESS, False),
        (S.CLOSED, S.NEW, False),
    ],
)
def test_transitions(current: IncidentStatus, target: IncidentStatus, allowed: bool):
    assert Incident(status=current).can_transition_to(target) is allowed


def test_every_status_has_rules():
    assert set(ALLOWED_TRANSITIONS) == set(IncidentStatus)
    assert ALLOWED_TRANSITIONS[S.CLOSED] == frozenset()
