"""
State machine for persistent operation tracking.
"""

import uuid
import time
from typing import List, Optional

from turbowifi.storage.models import OperationStateRecord
from turbowifi.storage.queries import Queries


class StateMachine:
    """Manages persistent state transitions for long-running operations."""

    def __init__(self, queries: Queries):
        self.queries = queries
        self.current_op: Optional[OperationStateRecord] = None

    def start_operation(self, operation_type: str) -> str:
        """Starts a new operation and persists the initial state."""
        op_id = str(uuid.uuid4())
        now = time.time()
        state = OperationStateRecord(
            operation_id=op_id,
            operation_type=operation_type,
            current_state="DETECTING_PLATFORM",
            started_at=now,
            updated_at=now,
            backup_ids_json=None,
            plan_json=None,
            error_message=None,
            metadata_json=None,
        )
        self.queries.upsert_operation_state(state)
        self.current_op = state
        return op_id

    def set_state(self, new_state: str, metadata_json: str | None = None) -> None:
        """Transitions to a new state and updates the database."""
        if not self.current_op:
            raise RuntimeError("No active operation to update.")

        self.current_op.current_state = new_state
        self.current_op.updated_at = time.time()
        if metadata_json is not None:
            self.current_op.metadata_json = metadata_json

        self.queries.upsert_operation_state(self.current_op)

    def fail_operation(self, error_message: str) -> None:
        """Marks the operation as failed."""
        if not self.current_op:
            return
        self.current_op.current_state = "ERROR"
        self.current_op.error_message = error_message
        self.current_op.updated_at = time.time()
        self.queries.upsert_operation_state(self.current_op)


def check_incomplete_operations(queries: Queries) -> List[OperationStateRecord]:
    """Check for operations that didn't complete cleanly."""
    return queries.get_pending_operations()
