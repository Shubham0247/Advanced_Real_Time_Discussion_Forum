from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_user_activity(
        self,
        *,
        user_id: UUID,
        range_key: str,
        type_key: str,
        skip: int,
        limit: int,
    ):
        time_clause = self._time_clause(range_key)
        type_clause = self._type_clause(type_key)
        query = text(
            f"""
            SELECT
                activity_type,
                thread_id,
                comment_id,
                title,
                preview,
                created_at
            FROM user_activity_view
            WHERE user_id = :user_id
            {time_clause}
            {type_clause}
            ORDER BY created_at DESC
            OFFSET :skip
            LIMIT :limit
            """
        )
        rows = self.db.execute(
            query,
            {
                "user_id": user_id,
                "skip": skip,
                "limit": limit,
            },
        ).mappings()
        return list(rows)

    def count_user_activity(self, *, user_id: UUID, range_key: str, type_key: str) -> int:
        time_clause = self._time_clause(range_key)
        type_clause = self._type_clause(type_key)
        query = text(
            f"""
            SELECT COUNT(*)
            FROM user_activity_view
            WHERE user_id = :user_id
            {time_clause}
            {type_clause}
            """
        )
        return self.db.scalar(query, {"user_id": user_id}) or 0

    @staticmethod
    def _time_clause(range_key: str) -> str:
        if range_key == "24h":
            return "AND created_at >= (NOW() - INTERVAL '24 hours')"
        if range_key == "7d":
            return "AND created_at >= (NOW() - INTERVAL '7 days')"
        if range_key == "1m":
            return "AND created_at >= (NOW() - INTERVAL '1 month')"
        return ""

    @staticmethod
    def _type_clause(type_key: str) -> str:
        if type_key == "like":
            return "AND activity_type IN ('thread.liked', 'comment.liked')"
        if type_key == "comment":
            return "AND activity_type IN ('comment.created', 'reply.created')"
        return ""
