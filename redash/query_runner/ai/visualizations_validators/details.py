from dataclasses import dataclass

from pydantic import BaseModel, Field

typeToColumnType = {
    "image": "integer",
    "json": "string",
    "link": "integer",
}


@dataclass
class Detail:
    name: str
    type: str
    description: str | None = None


class DetailsVisualization(BaseModel):
    columns: list[Detail] = Field(
        ...,
        description='A list of column details for the visualization in the form of { "name": "column_name", "type": "column_type", "description": "column_description" }.',
    )

    def to_dict(self):
        return {
            "columns": [
                {
                    "numberFormat": "0,0",
                    "nullValue": "null",
                    "booleanValues": ["false", "true"],
                    "imageUrlTemplate": "{{ @ }}",
                    "imageTitleTemplate": "{{ @ }}",
                    "imageWidth": "64" if col.type == "image" else "",
                    "imageHeight": "64" if col.type == "image" else "",
                    "linkUrlTemplate": "{{ @ }}",
                    "linkTextTemplate": "{{ @ }}",
                    "linkTitleTemplate": "{{ @ }}",
                    "linkOpenInNewTab": True,
                    "name": col.name,
                    "type": typeToColumnType[col.type],
                    "displayAs": col.type,
                    "visible": True,
                    "order": 100000 + i,
                    "title": col.name.replace("_", " ").title(),
                    "alignContent": "left",
                    "description": col.description or col.name.replace("_", " ").title(),
                    "allowHTML": False,
                    "highlightLinks": False,
                }
                for i, col in enumerate(self.columns)
            ]
        }
