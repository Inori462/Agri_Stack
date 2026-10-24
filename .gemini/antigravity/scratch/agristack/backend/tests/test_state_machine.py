import pytest
from app.core.state_machine import validate_state_transition
from app.models.project import ProjectStatus
from app.core.exceptions import InvalidStateTransitionError

def test_valid_project_lifecycle_transitions():
    # Sequential forward path
    validate_state_transition(ProjectStatus.DRAFT.value, ProjectStatus.SUBMITTED.value)
    validate_state_transition(ProjectStatus.SUBMITTED.value, ProjectStatus.UNDER_VERIFICATION.value)
    validate_state_transition(ProjectStatus.UNDER_VERIFICATION.value, ProjectStatus.VERIFIED.value)
    validate_state_transition(ProjectStatus.VERIFIED.value, ProjectStatus.OPEN_FOR_FUNDING.value)
    validate_state_transition(ProjectStatus.OPEN_FOR_FUNDING.value, ProjectStatus.FUNDED.value)
    validate_state_transition(ProjectStatus.FUNDED.value, ProjectStatus.IN_PROGRESS.value)
    validate_state_transition(ProjectStatus.IN_PROGRESS.value, ProjectStatus.HARVESTED.value)
    validate_state_transition(ProjectStatus.HARVESTED.value, ProjectStatus.SOLD.value)
    validate_state_transition(ProjectStatus.SOLD.value, ProjectStatus.SETTLED.value)
    validate_state_transition(ProjectStatus.SETTLED.value, ProjectStatus.CLOSED.value)

def test_invalid_state_transitions_are_blocked():
    # Skipping verification directly to funded must fail
    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(ProjectStatus.DRAFT.value, ProjectStatus.FUNDED.value)

    # Skipping from submitted to in_progress must fail
    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(ProjectStatus.SUBMITTED.value, ProjectStatus.IN_PROGRESS.value)

    # Moving backward from settled to draft must fail
    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(ProjectStatus.SETTLED.value, ProjectStatus.DRAFT.value)

    # Closed is terminal: any transition out of closed must fail
    with pytest.raises(InvalidStateTransitionError):
        validate_state_transition(ProjectStatus.CLOSED.value, ProjectStatus.OPEN_FOR_FUNDING.value)
