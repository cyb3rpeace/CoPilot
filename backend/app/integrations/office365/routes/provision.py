from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.auth.utils import AuthHandler
from app.db.db_session import get_db
from app.integrations.office365.schema.provision import ProvisionOffice365Request
from app.integrations.office365.schema.provision import ProvisionOffice365Response, ProvisionOffice365AuthKeys
from app.integrations.alert_escalation.services.general_alert import create_alert
from app.integrations.routes import get_customer_integrations_by_customer_code, find_customer_integration
from app.integrations.schema import CustomerIntegrationsResponse, CustomerIntegrations
from app.integrations.office365.services.provision import provision_office365
from typing import Dict

integration_office365_router = APIRouter()

async def get_customer_integration_response(customer_code: str, session: AsyncSession) -> CustomerIntegrationsResponse:
    customer_integration_response = await get_customer_integrations_by_customer_code(customer_code, session)
    if customer_integration_response.available_integrations == []:
        raise HTTPException(status_code=404, detail="Customer integration settings not found.")
    return customer_integration_response

def extract_office365_auth_keys(customer_integration: CustomerIntegrations) -> Dict[str, str]:
    office365_auth_keys = {}
    for subscription in customer_integration.integration_subscriptions:
        if subscription.integration_service.service_name == "Office365":
            for auth_key in subscription.integration_auth_keys:
                office365_auth_keys[auth_key.auth_key_name] = auth_key.auth_value
    if not office365_auth_keys:
        raise HTTPException(status_code=404, detail="No auth keys found for Office365 integration.")
    return office365_auth_keys


@integration_office365_router.post(
    "/provision",
    response_model=ProvisionOffice365Response,
    description="Provision Office365 integration for a customer.",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def provision_office365_route(provision_office365_request: ProvisionOffice365Request, session: AsyncSession = Depends(get_db)) -> ProvisionOffice365Response:

    customer_integration_response = await get_customer_integration_response(provision_office365_request.customer_code, session)

    customer_integration = await find_customer_integration(provision_office365_request.customer_code, provision_office365_request.integration_name, customer_integration_response)

    office365_auth_keys = extract_office365_auth_keys(customer_integration)

    auth_keys = ProvisionOffice365AuthKeys(**office365_auth_keys)

    return await provision_office365(provision_office365_request.customer_code, auth_keys, session)




