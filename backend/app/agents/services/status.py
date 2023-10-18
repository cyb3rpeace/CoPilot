from typing import List

from fastapi import HTTPException
from loguru import logger

from app.agents.schema.agents import OutdatedVelociraptorAgentsResponse
from app.agents.schema.agents import OutdatedWazuhAgentsResponse
from app.connectors.velociraptor.utils.universal import UniversalService
from app.db.db_session import session
from app.db.universal_models import Agents


def get_agent(agent_id: str) -> List[Agents]:
    """
    Retrieves a specific agent from the database using its ID.

    Args:
        agent_id (str): The ID of the agent to retrieve.

    Returns:
        AgentMetadata: The agent object if found, otherwise None.
    """
    try:
        return session.query(Agents).filter(Agents.agent_id == agent_id).first()
    except Exception as e:
        logger.error(f"Failed to fetch agent with agent_id {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent with agent_id {agent_id}: {e}")


def get_outdated_agents_wazuh() -> OutdatedWazuhAgentsResponse:
    """
    Retrieves all agents with outdated Wazuh agent versions from the database.

    Returns:
        List[dict]: A list of dictionaries where each dictionary represents the serialized data of an outdated agent.
    """
    wazuh_manager = get_agent("000")
    if wazuh_manager is None:
        logger.error("Wazuh Manager with agent_id '000' not found.")
        raise HTTPException(status_code=404, detail="Wazuh Manager with agent_id '000' not found.")
    try:
        outdated_wazuh_agents = (
            session.query(Agents).filter(Agents.agent_id != "000", Agents.wazuh_agent_version != wazuh_manager.wazuh_agent_version).all()
        )
        return {"message": "Outdated Wazuh agents fetched successfully.", "success": True, "outdated_wazuh_agents": outdated_wazuh_agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch outdated Wazuh agents: {e}")


def get_outdated_agents_velociraptor() -> OutdatedVelociraptorAgentsResponse:
    """
    Retrieves all agents with outdated Velociraptor client versions from the database.

    Returns:
        List[dict]: A list of dictionaries where each dictionary represents the serialized data of an outdated agent.
    """
    outdated_velociraptor_agents = []
    vql_server_version = "select * from config"
    server_version = UniversalService()._get_server_version(vql_server_version)
    try:
        agents = session.query(Agents).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch agents: {e}")
    try:
        for agent in agents:
            if agent.velociraptor_agent_version != server_version:
                outdated_velociraptor_agents.append(agent)
        return {
            "message": "Outdated Velociraptor agents fetched successfully.",
            "success": True,
            "outdated_velociraptor_agents": outdated_velociraptor_agents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch outdated Velociraptor agents: {e}")
