from flask import request
from funcy import project

from redash.handlers.base import BaseResource
from redash.query_runner.ai import AI


class EmptyQueryRunner:
    def __init__(self):
        self.type = "empty"
        self.configuration = {}

    @property
    def supports_ai_query_type(self):
        return "sql"


class AITypesListResource(BaseResource):
    def get(self):
        """Logic to list AI types"""

        self.record_event({"action": "view", "object_type": "ai_types", "type": "all"})

        return {"types": AI().supported_types}


class AIModelsListResource(BaseResource):
    def post(self):
        """Logic to list AI models for the given model"""
        req = request.get_json(True)
        params = project(req, ("type", "host", "token"))

        models = AI(
            query_runner=EmptyQueryRunner(),
            ai_type=params.get("type", "huggingface-local"),
            ai_host=params.get("host"),
            ai_token=params.get("token"),
        ).models
        params["token"] = None  # Prevent token from being stored in memory after initialization

        return {"models": models}
