from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.utils import AuthHandler
from app.connectors.velociraptor.schema.artifacts import ArtifactsResponse
from app.connectors.velociraptor.schema.artifacts import CollectArtifactBody
from app.connectors.velociraptor.schema.artifacts import CollectArtifactResponse
from app.connectors.velociraptor.schema.artifacts import OSPrefixEnum
from app.connectors.velociraptor.schema.artifacts import OSPrefixModel
from app.connectors.velociraptor.schema.artifacts import QuarantineBody
from app.connectors.velociraptor.schema.artifacts import QuarantineResponse
from app.connectors.velociraptor.schema.artifacts import RunCommandBody
from app.connectors.velociraptor.schema.artifacts import RunCommandResponse
from app.connectors.velociraptor.services.artifacts import get_artifacts
from app.connectors.velociraptor.services.artifacts import quarantine_host
from app.connectors.velociraptor.services.artifacts import run_artifact_collection
from app.connectors.velociraptor.services.artifacts import run_remote_command
from app.db.db_session import get_session, get_db
from app.db.universal_models import Agents

# App specific imports


velociraptor_artifacts_router = APIRouter()


# Get all valid OS prefixes
def get_valid_os_prefixes() -> List[str]:
    return [prefix.name.lower() for prefix in OSPrefixEnum]


# Verify the OS prefix exists and return the appropriate Enum value
def verify_os_prefix_exists(os_prefix: str) -> str:
    os_prefix_lower = os_prefix.lower()
    os_prefix_upper = os_prefix.upper()  # Convert to uppercase for Enum matching
    valid_os_prefixes = get_valid_os_prefixes()

    if os_prefix_lower not in valid_os_prefixes:
        raise HTTPException(status_code=400, detail=f"OS prefix {os_prefix} does not exist.")

    return OSPrefixEnum[os_prefix_upper].value  # Use the uppercase version for Enum matching


def get_os_prefix_from_os_name(os_name: str) -> str:
    # Use the OSPrefixModel to get the OS prefix from the OS name
    logger.info(f"Getting OS prefix from OS name {os_name}")
    os_prefix_model = OSPrefixModel(os_name=os_name)
    result = os_prefix_model.get_os_prefix()
    logger.info(f"OS prefix for OS name {os_name} is {result}")
    return result


# def get_velociraptor_id(hostname: str) -> str:
#     # Get the velociraptor_id from the hostname
#     logger.info(f"Getting velociraptor_id from hostname {hostname}")
#     agent = session.query(Agents).filter(Agents.hostname == hostname).first()
#     if not agent:
#         raise HTTPException(status_code=404, detail=f"Agent with hostname {hostname} not found")
#     velociraptor_id = agent.velociraptor_id
#     # If the velociraptor_id is `n/a`, raise an error
#     if velociraptor_id == "n/a":
#         raise HTTPException(status_code=404, detail=f"Velociraptor ID for hostname {hostname} is not available")
#     logger.info(f"velociraptor_id for hostname {hostname} is {velociraptor_id}")
#     return velociraptor_id


async def get_velociraptor_id(session: AsyncSession, hostname: str) -> str:
    logger.info(f"Getting velociraptor_id from hostname {hostname}")
    result = await session.execute(select(Agents).filter(Agents.hostname == hostname))
    agent = result.scalars().first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with hostname {hostname} not found")

    if agent.velociraptor_id == "n/a":
        raise HTTPException(status_code=404, detail=f"Velociraptor ID for hostname {hostname} is not available")

    logger.info(f"velociraptor_id for hostname {hostname} is {agent.velociraptor_id}")
    return agent.velociraptor_id


async def update_agent_quarantine_status(session: AsyncSession, quarantine_body: QuarantineBody, quarantine_response: QuarantineResponse):
    logger.info(f"Updating agent quarantine status for hostname {quarantine_body.hostname}")
    result = await session.execute(select(Agents).filter(Agents.hostname == quarantine_body.hostname))
    agent = result.scalars().first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with hostname {quarantine_body.hostname} not found")

    if quarantine_body.action == "quarantine":
        if quarantine_response.success:
            agent.quarantined = True
        else:
            raise HTTPException(status_code=500, detail=f"Failed to quarantine hostname {quarantine_body.hostname}")
    elif quarantine_body.action == "remove_quarantine":
        if quarantine_response.success:
            agent.quarantined = False
        else:
            raise HTTPException(status_code=500, detail=f"Failed to remove quarantine for hostname {quarantine_body.hostname}")

    await session.commit()

    logger.info(f"Agent quarantine status for hostname {quarantine_body.hostname} updated to {agent.quarantined}")

    return None


@velociraptor_artifacts_router.get(
    "",
    response_model=ArtifactsResponse,
    description="Get all artifacts",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_all_artifacts() -> ArtifactsResponse:
    logger.info("Fetching all artifacts")
    return await get_artifacts()


@velociraptor_artifacts_router.get(
    "/{os_prefix}",
    response_model=ArtifactsResponse,
    description="Get all artifacts for a specific OS prefix",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_all_artifacts_for_os_prefix(os_prefix: str = Depends(verify_os_prefix_exists)) -> ArtifactsResponse:
    logger.info(f"Fetching all artifacts for OS prefix {os_prefix}")
    # Get all the artifacts names that begin with the OS prefix
    artifacts = await get_artifacts()
    artifacts = artifacts.artifacts
    artifacts_for_os_prefix = [artifact for artifact in artifacts if artifact.name.startswith(os_prefix)]
    return ArtifactsResponse(success=True, message=f"All artifacts for OS prefix {os_prefix} retrieved", artifacts=artifacts_for_os_prefix)


@velociraptor_artifacts_router.get(
    "/hostname/{hostname}",
    response_model=ArtifactsResponse,
    description="Get all artifacts for a specific host's OS prefix",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_all_artifacts_for_hostname(hostname: str, session: AsyncSession = Depends(get_db)) -> ArtifactsResponse:
    logger.info(f"Fetching all artifacts for hostname {hostname}")

    # Asynchronous query to find the agent
    agent_result = await session.execute(select(Agents).filter(Agents.hostname == hostname))
    agent = agent_result.scalars().first()

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent with hostname {hostname} not found")

    os_prefix = get_os_prefix_from_os_name(os_name=agent.os.lower())
    if not os_prefix:
        raise HTTPException(status_code=404, detail=f"OS prefix of {agent.os.lower()} for hostname {hostname} not found")

    # Assuming get_all_artifacts_for_os_prefix is an async function
    result = await get_all_artifacts_for_os_prefix(os_prefix)

    return ArtifactsResponse(
        success=True,
        message=f"All available artifacts that can be ran for hostname {hostname} retrieved",
        artifacts=result.artifacts,
    )


# @velociraptor_artifacts_router.post(
#     "/collect",
#     response_model=CollectArtifactResponse,
#     description="Run an analyzer",
#     dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
# )
# async def collect_artifact(collect_artifact_body: CollectArtifactBody) -> CollectArtifactResponse:
#     logger.info(f"Received request to collect artifact {collect_artifact_body}")
#     # Check that provided artifact name applies for the provided hostname and use the `get_all_artifacts_for_hostname` function to get the list of artifacts
#     result = await get_all_artifacts_for_hostname(collect_artifact_body.hostname)
#     artifact_names = [artifact.name for artifact in result.artifacts]
#     if collect_artifact_body.artifact_name not in artifact_names:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Artifact name {collect_artifact_body.artifact_name} does not apply for hostname {collect_artifact_body.hostname} or does not exist",
#         )
#     # Add the velociraptor_id to the run_analyzer_body object
#     collect_artifact_body.velociraptor_id = get_velociraptor_id(collect_artifact_body.hostname)
#     # Run the analyzer
#     return run_artifact_collection(collect_artifact_body)


@velociraptor_artifacts_router.post(
    "/collect",
    response_model=CollectArtifactResponse,
    description="Run an analyzer",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def collect_artifact(
    collect_artifact_body: CollectArtifactBody,
    session: AsyncSession = Depends(get_db),
) -> CollectArtifactResponse:
    logger.info(f"Received request to collect artifact {collect_artifact_body}")
    result = await get_all_artifacts_for_hostname(collect_artifact_body.hostname, session)
    artifact_names = [artifact.name for artifact in result.artifacts]

    if collect_artifact_body.artifact_name not in artifact_names:
        raise HTTPException(
            status_code=400,
            detail=f"Artifact name {collect_artifact_body.artifact_name} does not apply for hostname {collect_artifact_body.hostname} or does not exist",
        )

    collect_artifact_body.velociraptor_id = await get_velociraptor_id(session, collect_artifact_body.hostname)

    # Assuming run_artifact_collection is an async function and takes a session as a parameter
    return await run_artifact_collection(collect_artifact_body)


@velociraptor_artifacts_router.post(
    "/command",
    response_model=RunCommandResponse,
    description="Run a remote command",
    dependencies=[Security(AuthHandler().get_current_user, scopes=["admin"])],
)
async def run_command(run_command_body: RunCommandBody, session: AsyncSession = Depends(get_db)) -> RunCommandResponse:
    logger.info(f"Received request to run command {run_command_body}")
    result = await get_all_artifacts_for_hostname(run_command_body.hostname, session)
    artifact_names = [artifact.name for artifact in result.artifacts]
    if run_command_body.artifact_name not in artifact_names:
        raise HTTPException(
            status_code=400,
            detail=f"Artifact name {run_command_body.artifact_name.value} does not apply for hostname {run_command_body.hostname} or does not exist",
        )
    # Add the velociraptor_id to the run_command_body object
    run_command_body.velociraptor_id = await get_velociraptor_id(session, run_command_body.hostname)
    # Run the command
    return await run_remote_command(run_command_body)


@velociraptor_artifacts_router.post(
    "/quarantine",
    response_model=QuarantineResponse,
    description="Quarantine a host",
    dependencies=[Security(AuthHandler().get_current_user, scopes=["admin"])],
)
async def quarantine(quarantine_body: QuarantineBody, session: AsyncSession = Depends(get_db)) -> QuarantineResponse:
    logger.info(f"Received request to quarantine host {quarantine_body}")
    result = await get_all_artifacts_for_hostname(quarantine_body.hostname, session)
    artifact_names = [artifact.name for artifact in result.artifacts]
    if quarantine_body.artifact_name not in artifact_names:
        raise HTTPException(
            status_code=400,
            detail=f"Artifact name {quarantine_body.artifact_name.value} does not apply for hostname {quarantine_body.hostname} or does not exist",
        )
    # Add the velociraptor_id to the run_command_body object
    # Add the velociraptor_id to the quarantine_body object
    quarantine_body.velociraptor_id = await get_velociraptor_id(session, quarantine_body.hostname)
    # Quarantine the host
    quarantine_response = await quarantine_host(quarantine_body)

    # If the host was successfully quarantined, update the database
    await update_agent_quarantine_status(session, quarantine_body, quarantine_response)

    return quarantine_response
