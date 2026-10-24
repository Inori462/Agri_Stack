from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user, require_roles
from ...models.user import User, UserRole
from ...models.project import Project, ProjectStatus
from ...models.escrow import EscrowMilestone
from ...models.share import ShareHolding
from ...schemas.project import ProjectCreate, ProjectResponse, ProjectTransitionRequest
from ...schemas.share import ShareHoldingResponse
from ...services.project_service import ProjectService
from ...core.exceptions import EntityNotFoundError, PermissionDeniedError

router = APIRouter(prefix="/projects", tags=["Crop Cycle Projects & Milestones"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    req: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new crop cycle project, division into digital shares,
    initializes 3 milestone escrow tiers (40/40/20), and farmer genesis shares.
    """
    if current_user.primary_role not in [UserRole.FARMER.value, UserRole.ADMIN.value]:
        raise PermissionDeniedError("Only verified farmers can create farm projects")
    return ProjectService.create_project(db=db, farmer=current_user, data=req)

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    crop_filter: Optional[str] = Query(None, alias="crop"),
    farmer_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists projects with optional filtering by state machine status, crop, or farmer."""
    query = db.query(Project)
    if status_filter:
        query = query.filter(Project.status == status_filter.upper())
    if crop_filter:
        query = query.filter(Project.crop_name.ilike(f"%{crop_filter}%"))
    if farmer_id:
        query = query.filter(Project.farmer_id == farmer_id)
    return query.order_by(Project.created_at.desc()).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves full details for a project including state machine transition history."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise EntityNotFoundError("Project not found")
    return project

@router.post("/{project_id}/transition", response_model=ProjectResponse)
def transition_project(
    project_id: UUID,
    req: ProjectTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes a state machine transition with RBAC and validation checks."""
    return ProjectService.transition_state(
        db=db,
        project_id=project_id,
        next_state=req.next_state.upper(),
        actor=current_user,
        rationale=req.rationale or req.remarks,
        metadata=req.metadata
    )

@router.get("/{project_id}/milestones")
def get_project_milestones(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists the 3 locked/released escrow milestones for a project."""
    milestones = (
        db.query(EscrowMilestone)
        .filter(EscrowMilestone.project_id == project_id)
        .order_by(EscrowMilestone.milestone_index.asc())
        .all()
    )
    return [
        {
            "id": str(m.id),
            "milestone_index": m.milestone_index,
            "name": m.name,
            "percentage_release": float(m.percentage_release),
            "amount_inr": float(m.amount_inr),
            "status": m.status,
            "proof_document_url": m.proof_document_url,
            "verification_notes": m.verification_notes,
            "released_at": m.released_at.isoformat() if m.released_at else None
        }
        for m in milestones
    ]

@router.post("/{project_id}/milestones/{milestone_index}/proof")
def submit_milestone_proof(
    project_id: UUID,
    milestone_index: int,
    proof_url: str = Query(..., description="Uploaded proof document / photo URL"),
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Farmer uploads verification evidence for unlocking a milestone."""
    m = ProjectService.submit_milestone_proof(
        db=db,
        project_id=project_id,
        milestone_index=milestone_index,
        farmer=current_user,
        proof_document_url=proof_url,
        notes=notes
    )
    return {"success": True, "milestone_status": m.status, "message": "Proof submitted for admin review"}

@router.post("/milestones/{milestone_id}/release")
def release_milestone(
    milestone_id: UUID,
    notes: Optional[str] = Query(None),
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
    db: Session = Depends(get_db)
):
    """Admin verifies evidence and unlocks escrow milestone funds to the farmer."""
    m = ProjectService.release_milestone_escrow(
        db=db,
        milestone_id=milestone_id,
        admin_user=admin_user,
        notes=notes
    )
    return {"success": True, "milestone_status": m.status, "message": "Escrow milestone funds released"}

@router.get("/{project_id}/shares", response_model=List[ShareHoldingResponse])
def get_project_cap_table(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns fractional digital shareholdings (cap table) for a farm project."""
    holdings = (
        db.query(ShareHolding)
        .filter(ShareHolding.project_id == project_id)
        .order_by(ShareHolding.share_count.desc())
        .all()
    )
    return holdings
