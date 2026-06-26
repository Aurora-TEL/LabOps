"""SQLAlchemy model exports.

Concrete models will be added in the next backend iteration based on
docs/05-database-design.md.
"""

from app.db.base import Base

__all__ = ["Base"]
