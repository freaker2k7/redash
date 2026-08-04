from enum import Enum
from time import time

from pydantic import BaseModel, Field

from redash import models
from redash.query_runner.ai import AI
from redash.query_runner.ai.visualizations_validators.counter import (
    CounterVisualization,
)
from redash.query_runner.ai.visualizations_validators.funnel import FunnelVisualization


class ConfQueryRunner:
    @property
    def supports_ai_query_type(self):
        return "conf"


class VisualizationInstanceType(Enum):
    __order__ = "COUNTER FUNNEL"
    # __order__ = "CHART COHORT COUNTER FUNNEL CHOROPLETH MAP PIVOT"
    # CHART = "CHART"
    # COHORT = "COHORT"
    COUNTER = CounterVisualization
    FUNNEL = FunnelVisualization
    # CHOROPLETH = "CHOROPLETH"
    # MAP = "MAP"
    # PIVOT = "PIVOT"


Schemas = {v.value.__class__.__name__: v.value.schema() for v in VisualizationInstanceType}

VisualizationType = Enum(
    "VisualizationType",
    {v.name.upper(): v.name.upper() for v in VisualizationInstanceType},
)


class VisualizationChooser(BaseModel):
    visualization_types: list[VisualizationType] = Field(
        ...,
        description="A list of visualization types to be generated based on the data. The available visualization types are COUNTER and FUNNEL.",
    )


class VisualizationTitles(BaseModel):
    name: str = Field(..., description="The name of the visualization.")
    description: str = Field(..., description="A brief description of the visualization.")


class VisualizationsGenerator:
    def __init__(self, data):
        self.data = data
        self.ai = AI(ConfQueryRunner())

    def choose_visualizations(self) -> list[str]:
        """
        Choose appropriate visualizations based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        choices = self.ai.prompt(
            VisualizationChooser,
            f"Here is the data: {self.data}",
            f"You are a helpful assistant that suggests appropriate visualizations based on the provided data. Your task is to analyze the data and choose the most suitable visualizations from the given list, choose appropriate visualizations from the following list: {[v.value for v in VisualizationType]}. Return the choices as a valid JSON object with the following structure: {VisualizationTitles.schema()}. Take into account the structures of the validators in order to create visualizations with the correct number of minimum fields: {Schemas}",
            [
                {"user": f"Here is the data: {self.data}", "assistant": '["COUNTER"]'},
            ],
        ).get("visualization_types", [])

        return {choice.value: VisualizationInstanceType[choice.value] for choice in choices}

    def get_visualization_titles(self, visualization) -> tuple[str, str]:
        """
        Generate titles and descriptions for visualizations based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        titles = self.ai.prompt(
            VisualizationTitles,
            f"Given the following data: {self.data}, generate a title and description for a {visualization.lower()} visualization. ",
            "You are a helpful assistant that generates titles and descriptions for visualizations based on the provided data. Your task is to analyze the data and generate a suitable title and description for the specified visualization type. Return the title and description as a valid JSON object with the following structure: {VisualizationTitles.schema()}. Do not include any explanations or additional text.",
            [
                {
                    "user": f"Given the following data: {self.data}, generate a title and description for a counter visualization.",
                    "assistant": '{"name": "User Counter", "description": "Counts the number of users."}',
                },
            ],
        )

        return (
            titles.get("name", f"AI generated {visualization} [{time()}]")[:100],
            titles.get("description", f"AI generated {visualization} visualization.")[:4096],
        )

    def get_visualization(self, visualization, visualization_class) -> models.Visualization:
        """
        Generate visualizations based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        return self.ai.prompt(
            visualization_class,
            f"Given the following data: {self.data}, generate a {visualization} visualization.",
            "You are a helpful assistant that generates visualizations based on the provided data. Your task is to analyze the data and generate a visualization of the specified type. Return the visualization as a valid JSON object with the following structure: {visualization_class.schema()}. Do not include any explanations or additional text.",
            [
                {
                    "user": f"Given the following data: {self.data}, generate a counter visualization.",
                    "assistant": '{"counterLabel": "User Count", "counterColName": "count", "countRow": false, "targetColName": "count"}',
                },
            ],
        )

    def get_visualizations(self) -> list:
        """
        Generate visualizations based on the data. This is a placeholder method
        and should be implemented with actual AI logic in subclasses.
        """

        visualizations_to_create = self.choose_visualizations()
        visualizations = []
        for visualization, visualization_class in visualizations_to_create.items():
            title, description = self.get_visualization_titles(visualization)

            visualizations.append(
                {
                    "name": title,
                    "description": description,
                    "type": visualization,
                    "options": self.get_visualization(visualization, visualization_class),
                }
            )
        return visualizations
