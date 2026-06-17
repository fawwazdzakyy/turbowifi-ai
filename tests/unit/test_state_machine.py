"""
Unit tests for state machine.
"""

from turbowifi.core.state_machine import StateMachine


def test_state_machine_flow(queries):
    sm = StateMachine(queries)

    # Start
    op_id = sm.start_operation("auto")
    assert sm.current_op.operation_id == op_id
    assert sm.current_op.current_state == "DETECTING_PLATFORM"

    # Transition
    sm.set_state("SCANNING")
    assert sm.current_op.current_state == "SCANNING"

    # Retrieve from DB
    persisted = queries.get_operation_state(op_id)
    assert persisted.current_state == "SCANNING"

    # Fail
    sm.fail_operation("Test error")
    assert sm.current_op.current_state == "ERROR"
    assert sm.current_op.error_message == "Test error"
