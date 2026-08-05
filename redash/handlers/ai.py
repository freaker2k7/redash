from redash.handlers.base import BaseResource
from redash.query_runner.ai import AI

# from redash.serializers import serialize_alert


class AITypesListResource(BaseResource):
    def get(self):
        # Implement logic to list AI models for the given engine
        self.record_event({"action": "view", "object_type": "ai_types", "type": "all"})
        return {"types": AI().supported_types}


class AIModelsListResource(BaseResource):
    def get(self, model):
        # Implement logic to list AI models for the given model
        self.record_event({"action": "view", "object_type": "ai_model", "model": model})
        return {"models": AI().models}
