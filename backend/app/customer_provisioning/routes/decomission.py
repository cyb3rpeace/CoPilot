from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.utils import AuthHandler
from app.customer_provisioning.schema.decomission import DecomissionCustomerResponse
from app.db.db_session import get_session
from app.db.universal_models import Customers, CustomersMeta
from app.customer_provisioning.services.decomission import decomission_wazuh_customer

# App specific imports


customer_decommissioning_router = APIRouter()


async def check_customermeta_exists(customer_name: str, session: AsyncSession = Depends(get_session)) -> CustomersMeta:
    """
    Check if a customer exists in the database.

    Args:
        customer_name (str): The name of the customer to check.
        session (AsyncSession, optional): The database session. Defaults to Depends(get_session).

    Returns:
        CustomersMeta: The customer object if found.

    Raises:
        HTTPException: If the customer is not found.
    """
    logger.info(f"Checking if customer {customer_name} exists")
    result = await session.execute(select(CustomersMeta).filter(CustomersMeta.customer_name == customer_name))
    customer_meta = result.scalars().first()

    if not customer_meta:
        raise HTTPException(status_code=404, detail=f"Customer: {customer_name} not found. Please create the customer first.")

    return customer_meta

@customer_decommissioning_router.post(
    "/decommission",
    response_model=DecomissionCustomerResponse,
    description="Decommission Customer",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def decommission_customer_route(
    _customer: CustomersMeta = Depends(check_customermeta_exists),
    session: AsyncSession = Depends(get_session),
):
    logger.info("Decommissioning customer")
    customer_decommission = await decomission_wazuh_customer(_customer, session=session)
    return customer_decommission
