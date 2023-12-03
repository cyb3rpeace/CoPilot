from typing import List

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from loguru import logger

from app.auth.utils import AuthHandler
from app.connectors.influxdb.schema.alerts import InfluxDBAlertsResponse
from app.connectors.influxdb.services.alerts import get_alerts
from app.connectors.influxdb.utils.universal import create_influxdb_client
from app.connectors.wazuh_indexer.schema.alerts import AlertsByHostResponse
from app.connectors.wazuh_indexer.schema.alerts import AlertsByRulePerHostResponse
from app.connectors.wazuh_indexer.schema.alerts import AlertsByRuleResponse
from app.connectors.wazuh_indexer.schema.alerts import AlertsSearchBody
from app.connectors.wazuh_indexer.schema.alerts import AlertsSearchResponse
from app.connectors.wazuh_indexer.schema.alerts import HostAlertsSearchBody
from app.connectors.wazuh_indexer.schema.alerts import HostAlertsSearchResponse
from app.connectors.wazuh_indexer.schema.alerts import IndexAlertsSearchBody
from app.connectors.wazuh_indexer.schema.alerts import IndexAlertsSearchResponse
from app.connectors.wazuh_indexer.services.alerts import get_alerts_by_host
from app.connectors.wazuh_indexer.services.alerts import get_alerts_by_rule
from app.connectors.wazuh_indexer.services.alerts import get_alerts_by_rule_per_host
from app.connectors.wazuh_indexer.services.alerts import get_host_alerts
from app.connectors.wazuh_indexer.services.alerts import get_index_alerts
from app.connectors.wazuh_indexer.utils.universal import collect_indices

# App specific imports


influxdb_alerts_router = APIRouter()


@influxdb_alerts_router.get(
    "/alerts",
    response_model=InfluxDBAlertsResponse,
    description="Get influxdb alerts",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_all_alerts():
    logger.info("Fetching all alerts from influxdb")
    return await get_alerts()
