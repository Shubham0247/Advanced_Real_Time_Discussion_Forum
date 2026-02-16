from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from pathlib import Path
import sys

# Allow running this script directly inside Docker/host shells.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pwdlib import PasswordHash
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.shared.database.session import SessionLocal
from backend.services.auth_service.app.core.seed import seed_roles
from backend.services.auth_service.app.models.role import Role
from backend.services.auth_service.app.models.user import User
from backend.services.discussion_service.app.models.comment import Comment
from backend.services.discussion_service.app.models.like import Like
from backend.services.discussion_service.app.models.thread import Thread


PASSWORD = "Password@123"
password_hash = PasswordHash.recommended()


@dataclass(frozen=True)
class UserSeed:
    username: str
    email: str
    full_name: str
    bio: str
    is_admin: bool = False


USER_SEEDS: list[UserSeed] = [
    UserSeed(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        bio="Platform administrator and cloud architect.",
        is_admin=True,
    ),
    UserSeed(
        username="alice",
        email="alice@example.com",
        full_name="Alice Johnson",
        bio="Backend engineer focused on APIs and distributed systems.",
    ),
    UserSeed(
        username="bob",
        email="bob@example.com",
        full_name="Bob Singh",
        bio="Frontend developer interested in performance and accessibility.",
    ),
    UserSeed(
        username="charlie",
        email="charlie@example.com",
        full_name="Charlie Lee",
        bio="Data engineer working with real-time analytics pipelines.",
    ),
    UserSeed(
        username="diana",
        email="diana@example.com",
        full_name="Diana Patel",
        bio="SRE working on reliability, observability, and incident response.",
    ),
]


THREAD_SEEDS: list[tuple[str, str]] = [
    (
        "Monolith vs Microservices in 2026",
        "How do you decide when to stay with a modular monolith vs splitting into microservices? Share decision points around team size, deployment speed, and operational complexity.",
    ),
    (
        "Practical WebSocket Scaling Strategies",
        "What architecture has worked for you when scaling WebSockets to thousands of concurrent users? Curious about sticky sessions, Redis pub/sub, and fanout patterns.",
    ),
    (
        "PostgreSQL Indexing Patterns That Actually Help",
        "Which index strategies gave you measurable latency improvements in production? Looking for examples with composite indexes, partial indexes, and query plans.",
    ),
    (
        "API Versioning Without Breaking Clients",
        "How are teams managing API evolution across mobile and web clients? Interested in deprecation workflows, schema validation, and compatibility guarantees.",
    ),
    (
        "Event-Driven Architecture Tradeoffs",
        "Where has event-driven design improved your product, and where did it introduce unnecessary complexity? Discuss retries, idempotency, and consumer drift.",
    ),
    (
        "Caching Layers for Read-Heavy Products",
        "For read-heavy feeds and dashboards, what cache strategy worked best for freshness and cost? Include TTL decisions and invalidation techniques.",
    ),
    (
        "Designing RBAC for Growing Teams",
        "What role model scales better in practice: simple coarse roles or permission-based scopes? Looking for patterns that remain maintainable over time.",
    ),
    (
        "When to Use Background Jobs vs Async Requests",
        "What criteria do you use to move work out of request-response flow? Please share queue setup, retries, and failure visibility practices.",
    ),
    (
        "Observability Stack Essentials",
        "If you had to keep only a minimal observability stack, what would it include? Traces, structured logs, metrics, SLOs, and alerting thresholds.",
    ),
    (
        "CI/CD Guardrails That Improve Quality",
        "Which pipeline checks have had the highest quality impact for your team? Curious about unit tests, integration tests, security scans, and deployment gates.",
    ),
    (
        "Feature Flags for Safer Releases",
        "How are you organizing feature flags to avoid long-term flag debt? Looking for naming conventions, rollout strategy, and cleanup workflows.",
    ),
    (
        "Secure Token Handling in SPAs",
        "What is your preferred token strategy for SPA auth in production? Discuss refresh flows, storage choices, and mitigation for token leakage.",
    ),
    (
        "Database Migration Process in Fast-Moving Teams",
        "How do you coordinate schema changes across multiple services without downtime? Interested in backward compatibility and rollout sequencing.",
    ),
    (
        "Rate Limiting Design for Public APIs",
        "What rate-limiting approach balances abuse prevention with developer experience? Share patterns for burst handling and per-user limits.",
    ),
    (
        "Search Relevance Tuning Beyond Keyword Match",
        "How are you improving relevance for forum-style search? Looking for practical ranking factors like recency, popularity, and semantic expansion.",
    ),
    (
        "Reliability Patterns for Notification Systems",
        "What architecture helps ensure notifications are delivered once and on time? Interested in at-least-once behavior, dedupe keys, and retries.",
    ),
    (
        "Container Security Baseline for Small Teams",
        "What minimum hardening steps should every team adopt for containerized apps? Share practices around image scanning, least privilege, and secrets.",
    ),
    (
        "Testing Strategy for Real-Time Discussion Platforms",
        "How do you test a system with REST endpoints plus realtime events end-to-end? Looking for practical test pyramid examples and tooling choices.",
    ),
]


def get_role(db: Session, role_name: str) -> Role:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if not role:
        raise RuntimeError(f"Role '{role_name}' is missing.")
    return role


def get_or_create_user(db: Session, spec: UserSeed) -> tuple[User, bool]:
    user = db.scalar(
        select(User).where(
            (User.username == spec.username) | (User.email == spec.email)
        )
    )
    created = False
    if not user:
        user = User(
            username=spec.username,
            email=spec.email,
            full_name=spec.full_name,
            bio=spec.bio,
            hashed_password=password_hash.hash(PASSWORD),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created = True
    else:
        updated = False
        if user.email != spec.email:
            conflict = db.scalar(
                select(User).where(
                    and_(User.email == spec.email, User.id != user.id)
                )
            )
            if not conflict:
                user.email = spec.email
                updated = True
        if user.full_name != spec.full_name:
            user.full_name = spec.full_name
            updated = True
        if user.bio != spec.bio:
            user.bio = spec.bio
            updated = True
        if updated:
            db.commit()
            db.refresh(user)
    return user, created


def ensure_user_has_roles(user: User, required_roles: Iterable[Role]) -> int:
    existing = {role.name for role in user.roles}
    added = 0
    for role in required_roles:
        if role.name not in existing:
            user.roles.append(role)
            existing.add(role.name)
            added += 1
    return added


def get_or_create_thread(
    db: Session,
    author_id,
    title: str,
    description: str,
) -> tuple[Thread, bool]:
    thread = db.scalar(
        select(Thread).where(
            and_(
                Thread.author_id == author_id,
                Thread.title == title,
            )
        )
    )
    created = False
    if not thread:
        thread = Thread(
            title=title,
            description=description,
            author_id=author_id,
            moderation_status="approved",
            is_deleted=False,
            is_locked=False,
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)
        created = True
    return thread, created


def get_or_create_comment(
    db: Session,
    thread_id,
    author_id,
    content: str,
    parent_id=None,
) -> tuple[Comment, bool]:
    if parent_id is None:
        condition = Comment.parent_id.is_(None)
    else:
        condition = Comment.parent_id == parent_id

    comment = db.scalar(
        select(Comment).where(
            and_(
                Comment.thread_id == thread_id,
                Comment.author_id == author_id,
                Comment.content == content,
                condition,
            )
        )
    )
    created = False
    if not comment:
        comment = Comment(
            thread_id=thread_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id,
            is_deleted=False,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        created = True
    return comment, created


def get_or_create_like(
    db: Session,
    user_id,
    *,
    thread_id=None,
    comment_id=None,
) -> bool:
    if (thread_id is None and comment_id is None) or (thread_id and comment_id):
        return False

    if thread_id:
        existing = db.scalar(
            select(Like).where(
                and_(Like.user_id == user_id, Like.thread_id == thread_id)
            )
        )
        if existing:
            return False
        db.add(Like(user_id=user_id, thread_id=thread_id))
    else:
        existing = db.scalar(
            select(Like).where(
                and_(Like.user_id == user_id, Like.comment_id == comment_id)
            )
        )
        if existing:
            return False
        db.add(Like(user_id=user_id, comment_id=comment_id))

    db.commit()
    return True


def build_comment_texts(title: str, thread_index: int) -> tuple[str, str, str]:
    comment_1 = (
        f"Great topic on '{title}'. In our team, we reduced incidents by defining "
        "clear ownership and measurable service-level objectives before scaling."
    )
    comment_2 = (
        "One challenge we hit was balancing delivery speed with architecture quality. "
        "A lightweight RFC process helped us align decisions early."
    )
    reply = (
        f"I agree. We also tracked latency and error-rate trends weekly for this area "
        f"and it improved decision quality for roadmap cycle {thread_index + 1}."
    )
    return comment_1, comment_2, reply


def seed() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        admin_role = get_role(db, "admin")
        member_role = get_role(db, "member")

        users: list[User] = []
        user_created_count = 0
        role_links_added = 0

        for spec in USER_SEEDS:
            user, created = get_or_create_user(db, spec)
            users.append(user)
            if created:
                user_created_count += 1

            required = [member_role, admin_role] if spec.is_admin else [member_role]
            role_links_added += ensure_user_has_roles(user, required)
            db.commit()

        non_admin_users = [u for u in users if u.username != "admin"]
        author_cycle = non_admin_users if non_admin_users else users

        threads: list[Thread] = []
        threads_created_count = 0
        comments_created_count = 0
        likes_created_count = 0

        for idx, (title, description) in enumerate(THREAD_SEEDS):
            author = author_cycle[idx % len(author_cycle)]
            thread, created = get_or_create_thread(
                db,
                author_id=author.id,
                title=title,
                description=description,
            )
            threads.append(thread)
            if created:
                threads_created_count += 1

            participants = [u for u in users if u.id != author.id]
            if len(participants) < 2:
                participants = users

            commenter_a = participants[idx % len(participants)]
            commenter_b = participants[(idx + 1) % len(participants)]

            c1_text, c2_text, reply_text = build_comment_texts(title, idx)
            c1, c1_created = get_or_create_comment(
                db,
                thread_id=thread.id,
                author_id=commenter_a.id,
                content=c1_text,
            )
            c2, c2_created = get_or_create_comment(
                db,
                thread_id=thread.id,
                author_id=commenter_b.id,
                content=c2_text,
            )
            reply_author = author
            _, reply_created = get_or_create_comment(
                db,
                thread_id=thread.id,
                author_id=reply_author.id,
                content=reply_text,
                parent_id=c1.id,
            )
            comments_created_count += int(c1_created) + int(c2_created) + int(reply_created)

            thread_likers = [u for u in users if u.id != author.id]
            thread_like_count = min(4, len(thread_likers))
            for liker_index in range(thread_like_count):
                liker = thread_likers[(idx + liker_index) % len(thread_likers)]
                if get_or_create_like(db, liker.id, thread_id=thread.id):
                    likes_created_count += 1

            for comment_idx, comment in enumerate((c1, c2)):
                comment_likers = [u for u in users if u.id != comment.author_id]
                comment_like_count = min(2, len(comment_likers))
                for liker_offset in range(comment_like_count):
                    liker = comment_likers[(idx + comment_idx + liker_offset) % len(comment_likers)]
                    if get_or_create_like(db, liker.id, comment_id=comment.id):
                        likes_created_count += 1

        print("Seed completed.")
        print(f"Users created: {user_created_count}")
        print(f"Role links added: {role_links_added}")
        print(f"Threads created: {threads_created_count}")
        print(f"Comments created: {comments_created_count}")
        print(f"Likes created: {likes_created_count}")
        print("Login password for seeded users: Password@123")
        print("Seeded usernames: admin, alice, bob, charlie, diana")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
