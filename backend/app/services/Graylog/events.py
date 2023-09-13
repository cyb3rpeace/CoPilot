# from datetime import datetime
from typing import Dict
from typing import List
from typing import Union

import requests
from loguru import logger

from app.services.Graylog.universal import UniversalService

# from typing import List


class EventsService:
    """
    A service class that encapsulates the logic for pulling event data from Graylog.
    """

    HEADERS: Dict[str, str] = {"X-Requested-By": "CoPilot"}

    def __init__(self):
        """
        Initializes the InputsService by collecting Graylog details.
        """
        (
            self.connector_url,
            self.connector_username,
            self.connector_password,
        ) = UniversalService().collect_graylog_details("Graylog")

    def collect_event_definitions(
        self,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[str, int]]]]]:
        """
        Collects the event definitions that are managed by Graylog.

        Returns:
            dict: A dictionary containing the success status, a message, and potentially a list of event definitions.
        """
        if self.connector_url is None or self.connector_username is None or self.connector_password is None:
            return {"message": "Failed to collect Graylog details", "success": False}

        event_definitions = self._collect_event_definitions()

        if event_definitions["success"]:
            return event_definitions

    def _collect_event_definitions(
        self,
    ) -> Dict[str, Union[bool, str, List[Dict[str, Union[str, int]]]]]:
        """
        Collects the event definitions that are managed by Graylog.

        Returns:
            dict: A dictionary containing the success status, a message, and potentially a list of event definitions.
        """
        try:
            event_definitions = requests.get(
                f"{self.connector_url}/api/events/definitions",
                headers=self.HEADERS,
                auth=(self.connector_username, self.connector_password),
                verify=False,
            )
            return {
                "message": "Successfully collected event definitions",
                "success": True,
                "event_definitions": event_definitions.json()["event_definitions"],
            }
        except Exception as e:
            logger.error(f"Failed to collect event definitions: {e}")
            return {"message": "Failed to collect event definitions", "success": False}
