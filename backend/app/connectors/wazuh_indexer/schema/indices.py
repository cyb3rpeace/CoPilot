from typing import Dict

from pydantic import BaseModel, Field


class Indices(BaseModel):
    indices_list: list
    success: bool
    message: str


class IndexConfigModel(BaseModel):
    SKIP_INDEX_NAMES: Dict[str, bool] = Field(
        default={
            "wazuh-statistics": True,
            "wazuh-monitoring": True,
        },
        description="A dictionary containing index names to be skipped and their skip status.",
    )

    def is_index_skipped(self, index_name: str) -> bool:
        """
        Checks whether the given index name should be skipped.

        Args:
            index_name (str): The name of the index to check.

        Returns:
            bool: True if the index should be skipped, False otherwise.
        """
        return any(index_name.startswith(skipped) for skipped in self.SKIP_INDEX_NAMES)

    def is_valid_index(self, index_name: str) -> bool:
        """
        Checks if the index name starts with "wazuh_" and is not in the SKIP_INDEX_NAMES list.

        Args:
            index_name (str): The name of the index to check.

        Returns:
            bool: True if the index is valid, False otherwise.
        """
        return index_name.startswith("wazuh") and not self.is_index_skipped(index_name)
