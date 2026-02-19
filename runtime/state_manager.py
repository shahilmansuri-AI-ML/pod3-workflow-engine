import json
from sqlalchemy import text


class StateManager:

    def initialize_state(self, session, execution_id):

        session.execute(
            text("""
            INSERT INTO execution_state (
                execution_id,
                state_snapshot
            )
            VALUES (
                :execution_id,
                '{}'
            )
            ON CONFLICT (execution_id)
            DO NOTHING
            """),
            {"execution_id": execution_id}
        )

    def update_state(self, session, execution_id, state):

        session.execute(
            text("""
            UPDATE execution_state
            SET state_snapshot = :state
            WHERE execution_id = :execution_id
            """),
            {
                "execution_id": execution_id,
                "state": json.dumps(state)
            }
        )

    def write_event(self, session, execution_id, event_type, payload):

        session.execute(
            text("""
            INSERT INTO execution_events (
                event_id,
                execution_id,
                event_type,
                source,
                event_payload
            )
            VALUES (
                gen_random_uuid(),
                :execution_id,
                :event_type,
                'executor',
                :payload
            )
            """),
            {
                "execution_id": execution_id,
                "event_type": event_type,
                "payload": json.dumps(payload)
            }
        )
