"""Service for managing PRD documents in the database."""

from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models.prd import PRD
from app.schemas.prd import PRDCreate, PRDUpdate, Format, TemplateType


class PRDService:
    """Service for managing PRD documents."""
    
    @staticmethod
    def create(
        db: Session, 
        prd_in: PRDCreate, 
        content: str, 
        user_id: uuid.UUID
    ) -> PRD:
        """
        Create a new PRD document.
        
        Args:
            db: Database session
            prd_in: PRD input data
            content: Generated PRD content
            user_id: ID of the user creating the PRD
            
        Returns:
            Created PRD
        """
        # Create PRD instance
        db_prd = PRD(
            title=prd_in.title,
            input_prompt=prd_in.input_prompt,
            content=content,
            format=prd_in.format,
            template_type=prd_in.template_type,
            user_id=user_id
        )
        
        # Add to database
        db.add(db_prd)
        db.commit()
        db.refresh(db_prd)
        
        return db_prd
    
    @staticmethod
    def get_by_id(db: Session, prd_id: uuid.UUID) -> Optional[PRD]:
        """
        Get a PRD by ID.
        
        Args:
            db: Database session
            prd_id: PRD ID
            
        Returns:
            PRD if found, None otherwise
        """
        return db.query(PRD).filter(PRD.id == prd_id).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[PRD]:
        """
        Get all PRDs for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of PRDs
        """
        return db.query(PRD).filter(
            PRD.user_id == user_id
        ).order_by(PRD.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, db_prd: PRD, prd_in: PRDUpdate) -> PRD:
        """
        Update a PRD.
        
        Args:
            db: Database session
            db_prd: Existing PRD model
            prd_in: PRD update data
            
        Returns:
            Updated PRD
        """
        # Update attributes
        for field, value in prd_in.dict(exclude_unset=True).items():
            setattr(db_prd, field, value)
        
        # Commit changes
        db.add(db_prd)
        db.commit()
        db.refresh(db_prd)
        
        return db_prd
    
    @staticmethod
    def delete(db: Session, db_prd: PRD) -> None:
        """
        Delete a PRD.
        
        Args:
            db: Database session
            db_prd: PRD model to delete
        """
        db.delete(db_prd)
        db.commit()
