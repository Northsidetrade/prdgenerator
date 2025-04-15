"""PRD generation endpoint module."""

import uuid
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.db.session import get_db
from app.models.user import User
from app.schemas.prd import PRDCreate, PRDResponse, PRDUpdate, PRDInDB
from app.services.llm_service import generate_prd_content, ModelProvider
from app.services.prd_service import PRDService

router = APIRouter()


@router.post("/generate", response_model=PRDResponse)
async def generate_prd(
    request: Request,
    prd_data: PRDCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate a new PRD from user input and save it to the database.
    
    This endpoint takes user input and template selection,
    then generates a Product Requirements Document using AI.
    """
    try:
        # Determine if we're in a test environment
        provider = ModelProvider.TEST if hasattr(request.app.state, "testing") and request.app.state.testing else None
        
        # Generate PRD content using LLM service
        content = await generate_prd_content(
            title=prd_data.title,
            input_prompt=prd_data.input_prompt,
            template_type=prd_data.template_type,
            output_format=prd_data.format,
            provider=provider
        )
        
        # Save the PRD to the database
        db_prd = PRDService.create(
            db=db,
            prd_in=prd_data,
            content=content,
            user_id=current_user.id
        )
        
        # Create response
        return {
            "id": db_prd.id,
            "title": db_prd.title,
            "content": db_prd.content,
            "format": db_prd.format,
            "created_at": db_prd.created_at,
            "template_type": db_prd.template_type,
            "user_id": db_prd.user_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PRD generation failed: {str(e)}")


@router.get("/", response_model=List[PRDResponse])
def read_prds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve PRDs for the current user.
    
    Args:
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of PRDs belonging to the current user
    """
    prds = PRDService.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return prds


@router.get("/{prd_id}", response_model=PRDResponse)
def read_prd(
    prd_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific PRD by ID.
    
    Args:
        prd_id: PRD ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        PRD if found and belongs to the current user
        
    Raises:
        HTTPException: If PRD not found or doesn't belong to user
    """
    prd = PRDService.get_by_id(db=db, prd_id=prd_id)
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRD not found",
        )
    if prd.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return prd


@router.delete("/{prd_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prd(
    prd_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a PRD by ID.
    
    Args:
        prd_id: PRD ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If PRD not found or doesn't belong to user
    """
    prd = PRDService.get_by_id(db=db, prd_id=prd_id)
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRD not found",
        )
    if prd.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    PRDService.delete(db=db, db_prd=prd)
