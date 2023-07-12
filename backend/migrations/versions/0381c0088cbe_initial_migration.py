"""Initial migration.

Revision ID: 0381c0088cbe
Revises:
Create Date: 2023-07-11 13:24:04.087035

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "0381c0088cbe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if "agent_metadata" not in inspector.get_table_names():
        op.create_table(
            "agent_metadata",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("agent_id", sa.String(length=100), nullable=True),
            sa.Column("ip_address", sa.String(length=100), nullable=True),
            sa.Column("os", sa.String(length=100), nullable=True),
            sa.Column("hostname", sa.String(length=100), nullable=True),
            sa.Column("critical_asset", sa.Boolean(), nullable=True),
            sa.Column("last_seen", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "artifact" not in inspector.get_table_names():
        op.create_table(
            "artifact",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("artifact_name", sa.String(length=100), nullable=True),
            sa.Column("artifact_results", sa.TEXT(), nullable=True),
            sa.Column("hostname", sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "case" not in inspector.get_table_names():
        op.create_table(
            "case",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("case_id", sa.Integer(), nullable=True),
            sa.Column("case_name", sa.String(length=100), nullable=True),
            sa.Column("agents", sa.String(length=1000), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "connectors" not in inspector.get_table_names():
        op.create_table(
            "connectors",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("connector_name", sa.String(length=100), nullable=True),
            sa.Column("connector_type", sa.String(length=100), nullable=True),
            sa.Column("connector_url", sa.String(length=100), nullable=True),
            sa.Column("connector_last_updated", sa.DateTime(), nullable=True),
            sa.Column("connector_username", sa.String(length=100), nullable=True),
            sa.Column("connector_password", sa.String(length=100), nullable=True),
            sa.Column("connector_api_key", sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("connector_name"),
        )
    if "connectors_available" not in inspector.get_table_names():
        op.create_table(
            "connectors_available",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("connector_name", sa.String(length=100), nullable=True),
            sa.Column("connector_description", sa.String(length=100), nullable=True),
            sa.Column("connector_supports", sa.String(length=100), nullable=True),
            sa.Column("connector_configured", sa.Boolean(), nullable=True),
            sa.Column("connector_verified", sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("connector_name"),
        )
    if "disabled_rules" not in inspector.get_table_names():
        op.create_table(
            "disabled_rules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("rule_id", sa.String(length=100), nullable=True),
            sa.Column("previous_level", sa.String(length=1000), nullable=True),
            sa.Column("new_level", sa.String(length=1000), nullable=True),
            sa.Column("reason_for_disabling", sa.String(length=100), nullable=True),
            sa.Column("date_disabled", sa.DateTime(), nullable=True),
            sa.Column("length_of_time", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "graylog_metrics_allocation" not in inspector.get_table_names():
        op.create_table(
            "graylog_metrics_allocation",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("input_usage", sa.Float(), nullable=True),
            sa.Column("output_usage", sa.Float(), nullable=True),
            sa.Column("processor_usage", sa.Float(), nullable=True),
            sa.Column("input_1_sec_rate", sa.Float(), nullable=True),
            sa.Column("output_1_sec_rate", sa.Float(), nullable=True),
            sa.Column("total_input", sa.Float(), nullable=True),
            sa.Column("total_output", sa.Float(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "wazuh_indexer_allocation" not in inspector.get_table_names():
        op.create_table(
            "wazuh_indexer_allocation",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("node", sa.String(length=100), nullable=True),
            sa.Column("disk_used", sa.Float(), nullable=True),
            sa.Column("disk_available", sa.Float(), nullable=True),
            sa.Column("disk_total", sa.Float(), nullable=True),
            sa.Column("disk_percent", sa.Float(), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "sublime_alerts" not in inspector.get_table_names():
        op.create_table(
            "sublime_alerts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("message_id", sa.String(length=1000), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("wazuh_indexer_allocation")
    op.drop_table("graylog_metrics_allocation")
    op.drop_table("disabled_rules")
    op.drop_table("connectors_available")
    op.drop_table("connectors")
    op.drop_table("case")
    op.drop_table("artifact")
    op.drop_table("agent_metadata")
    # ### end Alembic commands ###
