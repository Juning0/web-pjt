from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/posts", tags=["comments"])


@router.post("/{post_id}/comments", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    post_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db)
):
    """댓글 작성."""
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "게시글을 찾을 수 없습니다.")
    return crud.create_comment(db, post_id, data)


@router.post("/comments/{comment_id}/delete", status_code=204)
def delete_comment(
    comment_id: int, body: schemas.PasswordCheck, db: Session = Depends(get_db)
):
    """댓글 삭제 — 비밀번호 확인."""
    comment = crud.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "댓글을 찾을 수 없습니다.")
    if comment.password != body.password:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "비밀번호가 일치하지 않습니다.")
    crud.delete_comment(db, comment)
