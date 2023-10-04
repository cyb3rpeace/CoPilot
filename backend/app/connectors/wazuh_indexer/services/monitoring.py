from typing import Dict, Any
from sqlmodel import Session, select
from app.connectors.models import Connectors
from elasticsearch7 import Elasticsearch
from loguru import logger
from app.db.db_session import engine
from typing import Union
import requests
from app.connectors.schema import ConnectorResponse
from app.connectors.utils import get_connector_info_from_db
from app.connectors.wazuh_indexer.utils.universal import create_wazuh_indexer_client, format_node_allocation, format_indices_stats, format_shards
from app.connectors.wazuh_indexer.schema.monitoring import ClusterHealthResponse, ClusterHealth, NodeAllocationResponse, NodeAllocation, IndicesStatsResponse, IndicesStats, Shards, ShardsResponse


def cluster_healthcheck() -> Union[ClusterHealthResponse, Dict[str, str]]:
    """
    Returns the cluster health of the Wazuh Indexer service.

    Returns:
        ElasticsearchResponse: A Pydantic model containing the cluster health of the Wazuh Indexer service.

    Raises:
        Exception: An exception is raised if the cluster health cannot be retrieved.
    """
    logger.info("Collecting Wazuh Indexer healthcheck")
    es_client = create_wazuh_indexer_client('Wazuh-Indexer')
    try:
        cluster_health_data = es_client.cluster.health()
        cluster_health_model = ClusterHealth(**cluster_health_data)
        return ClusterHealthResponse(
            cluster_health=cluster_health_model,
            success=True,
            message="Successfully collected Wazuh Indexer cluster health"
        )
    except Exception as e:
        logger.error(f"Cluster health check failed with error: {e}")
        return {"success": False, "message": f"Cluster health check failed with error: {e}"}
    
def node_allocation() -> Union[NodeAllocationResponse, Dict[str, bool]]:
    """
    Returns the node allocation of the Wazuh Indexer service.

    Returns:
        ElasticsearchResponse: A Pydantic model containing the node allocation of the Wazuh Indexer service.

    Raises:
        Exception: An exception is raised if the node allocation cannot be retrieved.
    """
    logger.info("Collecting Wazuh Indexer node allocation")
    es_client = create_wazuh_indexer_client('Wazuh-Indexer')
    try:
        raw_node_allocation_data = es_client.cat.allocation(format="json")
        logger.info(raw_node_allocation_data)
        
        formatted_node_allocation_data = format_node_allocation(raw_node_allocation_data)
        
        node_allocation_models = [NodeAllocation(**node) for node in formatted_node_allocation_data]

        return NodeAllocationResponse(
            node_allocation=node_allocation_models,
            success=True,
            message="Successfully collected Wazuh Indexer node allocation"
        )
    except Exception as e:
        logger.error(f"Node allocation check failed with error: {e}")
        return {"success": False, "message": f"Node allocation check failed with error: {e}"}

def indices_stats() -> Union[IndicesStatsResponse, Dict[str, str]]:
    """
    Returns the indices stats of the Wazuh Indexer service.

    Returns:
        ElasticsearchResponse: A Pydantic model containing the indices stats of the Wazuh Indexer service.

    Raises:
        Exception: An exception is raised if the indices stats cannot be retrieved.
    """
    logger.info("Collecting Wazuh Indexer indices stats")
    es_client = create_wazuh_indexer_client('Wazuh-Indexer')
    try:
        raw_indices_stats_data = es_client.cat.indices(format="json")

        formatted_indices_stats_data = format_indices_stats(raw_indices_stats_data)
        
        indices_stats_models = [IndicesStats(**index) for index in formatted_indices_stats_data]

        return IndicesStatsResponse(
            indices_stats=indices_stats_models,
            success=True,
            message="Successfully collected Wazuh Indexer indices stats"
        )
    except Exception as e:
        logger.error(f"Indices stats check failed with error: {e}")
        return {"success": False, "message": f"Indices stats check failed with error: {e}"}
    
def shards() -> Union[ShardsResponse, Dict[str, str]]:
    """
    Returns the shards of the Wazuh Indexer service.

    Returns:
        ElasticsearchResponse: A Pydantic model containing the shards of the Wazuh Indexer service.

    Raises:
        Exception: An exception is raised if the shards cannot be retrieved.
    """
    logger.info("Collecting Wazuh Indexer shards")
    es_client = create_wazuh_indexer_client('Wazuh-Indexer')
    try:
        raw_shards_data = es_client.cat.shards(format="json")

        formatted_shards_data = format_shards(raw_shards_data)

        shard_models = [Shards(**shard) for shard in formatted_shards_data]

        return ShardsResponse(
            shards=shard_models,
            success=True,
            message="Successfully collected Wazuh Indexer shards"
        )
    except Exception as e:
        logger.error(f"Shards check failed with error: {e}")
        return {"success": False, "message": f"Shards check failed with error: {e}"}