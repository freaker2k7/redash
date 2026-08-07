import logging
from enum import Enum

from pydantic import BaseModel, Field

from redash.query_runner.ai import AI

logger = logging.getLogger(__name__)


class ConfQueryRunner:
    def __init__(self):
        self.type = "conf"
        self.configuration = {}

    @property
    def supports_ai_query_type(self):
        return "conf"


class AlertOperators(Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="


class AlertSelectors(Enum):
    FIRST = "first"
    MIN = "min"
    MAX = "max"


class AlertConfiguration(BaseModel):
    name: str = Field(..., description="The title of the alert.")
    column: str = Field(..., description="The name of the column to which the condition applies.")
    op: AlertOperators = Field(..., description="The operator used for the condition (e.g., '>', '<', '=', '!=', '>=', '<=').")
    selector: AlertSelectors = Field(..., description="The selector used for the condition (e.g., 'first', 'last', etc.).")
    value: float = Field(..., description="The value against which the column is compared.")

    def to_dict(self):
        return {
            "name": self.name,
            "column": self.column,
            "op": self.op.value,
            "selector": self.selector.value,
            "value": self.value,
            "muted": False,
        }


class AlertConfigurations(BaseModel):
    alerts: list[AlertConfiguration] = Field(..., description="The list of alert configurations.")

    def to_dict(self):
        return {
            "alerts": [alert.to_dict() for alert in self.alerts],
        }


class AlertsGenerator:
    def __init__(self, query_runner, data, query):
        self.query_runner = query_runner
        self.ai = AI(ConfQueryRunner())
        self.query = query
        self.data = str(
            {
                "columns": data.get("columns", []),
                "row_count": len(data.get("rows", [])),
            }
        )

    def choose_alerts(self) -> dict[str, AlertConfiguration]:
        """
        Choose appropriate alerts based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        choices = self.ai.prompt(
            AlertConfigurations,
            f"Here is the data: {self.data}\n\nHere is the query: {self.query}",
            f"You are a helpful assistant that suggests appropriate alerts based on the provided data. Your task is to analyze the data and choose the most suitable alerts from the given list. Return the results as a valid JSON object with the following structure: {AlertConfigurations.model_json_schema()}. Do not include any explanations or additional text.",
            [
                {
                    "user": "Here is the data: {'columns': [{'name': 'count', 'friendly_name': 'count', 'type': 'integer'}], 'row_count': 1}",
                    "assistant": '{"alerts": [{"name": "We crossed 1000 users", "column": "count", "op": ">", "selector": "first", "value": 1000}, {"name": "We reached a million users", "column": "count", "op": "==", "selector": "first", "value": 1000000}]}',
                },
            ],
        ).get("alerts", [])

        logger.debug(f"AI suggested alerts: {choices}")

        return {choice["name"]: choice for choice in choices}

    def get_alerts(self) -> list:
        """
        Generate alerts based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        alerts_to_create = self.choose_alerts()
        alerts = []
        for alert_name, alert_class in alerts_to_create.items():
            del alert_class["name"]  # Remove the name from the alert_class dictionary
            alerts.append(
                {
                    "name": alert_name,
                    "options": alert_class,
                }
            )

        logger.debug(f"AI generated alerts: {alerts}")

        return alerts
