from typing import Dict, Set, Optional
from ..models.project import ProjectStatus
from .exceptions import InvalidStateTransitionError

# Directed graph of allowed transitions in AgriStack project lifecycle
VALID_TRANSITIONS: Dict[str, Set[str]] = {
    ProjectStatus.DRAFT.value: {
        ProjectStatus.SUBMITTED.value,
    },
    ProjectStatus.SUBMITTED.value: {
        ProjectStatus.UNDER_VERIFICATION.value,
        ProjectStatus.FLAGGED.value,
        ProjectStatus.REJECTED.value,
    },
    ProjectStatus.UNDER_VERIFICATION.value: {
        ProjectStatus.VERIFIED.value,
        ProjectStatus.FLAGGED.value,
        ProjectStatus.REJECTED.value,
    },
    ProjectStatus.VERIFIED.value: {
        ProjectStatus.OPEN_FOR_FUNDING.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.OPEN_FOR_FUNDING.value: {
        ProjectStatus.FUNDED.value,
        ProjectStatus.REJECTED.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.FUNDED.value: {
        ProjectStatus.IN_PROGRESS.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.IN_PROGRESS.value: {
        ProjectStatus.HARVESTED.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.HARVESTED.value: {
        ProjectStatus.SOLD.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.SOLD.value: {
        ProjectStatus.SETTLED.value,
        ProjectStatus.FLAGGED.value,
    },
    ProjectStatus.SETTLED.value: {
        ProjectStatus.CLOSED.value,
    },
    ProjectStatus.FLAGGED.value: {
        ProjectStatus.UNDER_VERIFICATION.value,
        ProjectStatus.REJECTED.value,
        ProjectStatus.IN_PROGRESS.value,
    },
    ProjectStatus.REJECTED.value: {
        ProjectStatus.DRAFT.value,  # Allowed only if farmer addresses rejection remarks
    },
    ProjectStatus.CLOSED.value: set(),  # Terminal state
}

def validate_state_transition(current_state: str, next_state: str) -> None:
    """
    Validates if transitioning from current_state to next_state is legal.
    Raises InvalidStateTransitionError if the transition violates the state machine.
    """
    allowed_next_states = VALID_TRANSITIONS.get(current_state, set())
    if next_state not in allowed_next_states:
        raise InvalidStateTransitionError(
            f"Illegal state transition from '{current_state}' to '{next_state}'. "
            f"Allowed next states: {sorted(list(allowed_next_states)) or 'None (Terminal state)'}"
        )

class StateMachine:
    @staticmethod
    def transition(db, project, new_status: str, actor_id=None, notes: str = None):
        validate_state_transition(project.status, new_status)
        project.status = new_status
        db.commit()
        return project
