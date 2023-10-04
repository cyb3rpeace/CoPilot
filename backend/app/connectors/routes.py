from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Union
from app.connectors.schema import ConnectorResponse, ConnectorListResponse, VerifyConnectorResponse, ConnectorsListResponse, UpdateConnector
from app.connectors.services import ConnectorServices
from loguru import logger
from app.db.db_session import session

## Auth Things
from fastapi import APIRouter, HTTPException, Security, security, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.schema.auth import UserResponse, UserLoginResponse

from app.auth.routes.auth import auth_handler
from app.db.db_session import session
from app.auth.models.users import UserInput, User, UserLogin
from app.auth.services.universal import select_all_users, find_user
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

connector_router = APIRouter()

@connector_router.get("", response_model=ConnectorsListResponse, description="Fetch all available connectors")
async def get_connectors(user=Depends(auth_handler.get_current_user)) -> ConnectorListResponse:
    """
    Fetch all available connectors from the database.

    This endpoint retrieves all the connectors stored in the database and returns them
    along with a success status and message.

    Returns:
        ConnectorListResponse: A Pydantic model containing a list of connectors and additional metadata.

    Raises:
        HTTPException: An exception with a 404 status code is raised if no connectors are found.
    """
    logger.info(f"Fetching all connectors for user: {user.username}")
    if not user.is_admin:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    
    connectors = ConnectorServices.fetch_all_connectors() 
    if connectors:
        return {
            "connectors": connectors,
            "success": True,
            "message": "Connectors fetched successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="No connectors found")

@connector_router.get("/{connector_id}", response_model=ConnectorListResponse, description="Fetch a specific connector")
async def get_connector(connector_id: int) -> Union[ConnectorResponse, HTTPException]:
    """
    Fetch a specific connector by its ID.

    This endpoint retrieves a connector identified by `connector_id` from the database.

    Args:
        connector_id (int): The unique identifier for the connector to fetch.

    Returns:
        ConnectorResponse: A Pydantic model representing the fetched connector.

    Raises:
        HTTPException: An exception with a 404 status code is raised if the connector is not found.
    """
    connector = ConnectorServices.fetch_connector_by_id(connector_id)
    if connector is not None:
        return {
            "connector": connector,
            "success": True,
            "message": "Connector fetched successfully"
        }
    else:
        raise HTTPException(status_code=404, detail=f"No connector found for ID: {connector_id}".format(connector_id=connector_id))
    
@connector_router.post("/verify/{connector_id}", response_model=VerifyConnectorResponse, description="Verify a connector. Makes an API call to the connector to verify it is working.")
async def verify_connector(connector_id: int) -> Union[VerifyConnectorResponse, HTTPException]:
    """
    Verify a connector by its ID.

    This endpoint verifies a connector identified by `connector_id` by making an API call to the connector.

    Args:
        connector_id (int): The unique identifier for the connector to verify.

    Returns:
        ConnectorResponse: A Pydantic model representing the verified connector.

    Raises:
        HTTPException: An exception with a 404 status code is raised if the connector is not found.
    """
    connector = ConnectorServices.verify_connector_by_id(connector_id)
    if connector is not None:
        logger.info(f"Connector verified successfully: {connector}")
        return connector
    else:
        raise HTTPException(status_code=404, detail=f"No connector found for ID: {connector_id}".format(connector_id=connector_id))
    

@connector_router.put("/{connector_id}", response_model=ConnectorListResponse, description="Update a connector")
async def update_connector(connector_id: int, connector: UpdateConnector) -> ConnectorListResponse:
    """
    Update a connector by its ID.

    This endpoint updates a connector identified by `connector_id` in the database.

    Args:
        connector_id (int): The unique identifier for the connector to update.
        connector (ConnectorListResponse): The updated connector data.

    Returns:
        ConnectorListResponse: A Pydantic model representing the updated connector.

    Raises:
        HTTPException: An exception with a 404 status code is raised if the connector is not found.
    """
    updated_connector = ConnectorServices.update_connector_by_id(connector_id, connector)
    if updated_connector is not None:
        return {
            "connector": updated_connector,
            "success": True,
            "message": "Connector updated successfully"
        }
    else:
        raise HTTPException(status_code=404, detail=f"No connector found for ID: {connector_id}".format(connector_id=connector_id))
    

@connector_router.post("/upload/{connector_id}", description="Upload a YAML file for a specific connector")
async def upload_yaml_file(connector_id: int, file: UploadFile = File(...)) -> dict:
    """
    Upload a YAML file for a specific connector ID.

    This endpoint allows you to upload a `.yaml` file for a specific connector
    identified by `connector_id`.

    Args:
        connector_id (int): The unique identifier for the connector.
        file (UploadFile): The `.yaml` file to be uploaded.

    Returns:
        dict: A dictionary with a success message and other information.

    Raises:
        HTTPException: An exception with a 400 status code is raised if the file format is incorrect or connector ID is not 6.
    """
    if connector_id != 6:
        raise HTTPException(status_code=400, detail="Only the Velociraptor connector is allowed for YAML file uploads.")
    if not file.filename.endswith(".yaml"):
        raise HTTPException(status_code=400, detail="Only .yaml files are allowed.")
    try:
        save_file_result = ConnectorServices.save_file(file)
        if save_file_result:
            return {"success": True, "message": "File uploaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

