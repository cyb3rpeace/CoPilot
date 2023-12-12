from app.integrations.alert_creation.general.schema.alert import CreateAlertRequest
from app.integrations.alert_creation.general.schema.alert import CreateAlertResponse
from fastapi import APIRouter
from fastapi import HTTPException
from app.db.db_session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.future import select
from app.integrations.alert_creation.models.alert_settings import AlertCreationSettings
from loguru import logger

general_alerts_router = APIRouter()


async def invalid_rule_id(create_alert_request: CreateAlertRequest, session: AsyncSession) -> bool:
    logger.info(f"Checking if rule_id: {create_alert_request.rule_id} is valid for customer: {create_alert_request.agent_labels_customer}")

    result = await session.execute(
        select(AlertCreationSettings).where(
            AlertCreationSettings.customer_code == create_alert_request.agent_labels_customer
        )
    )
    settings = result.scalars().first()

    if settings and str(create_alert_request.rule_id) in (settings.excluded_wazuh_rules or '').split(','):
        return True

    return False



@general_alerts_router.post(
    "/general",
    response_model=CreateAlertResponse,
    description="Create a general alert in IRIS.",
)
async def create_general_alert(
    create_alert_request: CreateAlertRequest,
    session: AsyncSession = Depends(get_session),
):
    logger.info(f"create_alert_request: {create_alert_request.dict()}")

    if await invalid_rule_id(create_alert_request, session):
        logger.info(f"Invalid rule_id: {create_alert_request.rule_id}")
        raise HTTPException(status_code=200, detail="Invalid rule_id")

    logger.info(f"Rule id is valid: {create_alert_request.rule_id}")
    # Rest of your logic here...
    return None


