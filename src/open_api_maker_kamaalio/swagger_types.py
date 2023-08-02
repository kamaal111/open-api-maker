from typing import Any, Literal, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .enums import (
        DefinitionTypes,
        DefinitionNames,
        SwaggerPathMethods,
        SwaggerPaths,
        SwaggerParameterTypes,
    )


class SwaggerDefinition(TypedDict, total=False):
    type: "DefinitionTypes"
    properties: dict[str, "SwaggerDefinition"] | None
    required: list[str]


class SwaggerInfoLicense(TypedDict):
    name: str
    url: str


class SwaggerInfo(TypedDict):
    contact: dict[str, Any]
    description: str
    license: SwaggerInfoLicense
    title: str
    version: str


SwaggerReferenceSchema = TypedDict("SwaggerReferenceSchema", {"$ref": str | None})

SwaggerArraySchema = TypedDict(
    "SwaggerArraySchema",
    {"items": "SwaggerReferenceSchema" | None, "type": Literal["array"]},
)


class SwaggerResponse(TypedDict):
    description: str
    schema: SwaggerReferenceSchema | SwaggerArraySchema


SwaggerParameter = TypedDict(
    "SwaggerParameter",
    {
        "description": str,
        "example": str | None,
        "in": "SwaggerParameterTypes",
        "name": str,
        "required": bool,
        "schema": SwaggerReferenceSchema | SwaggerArraySchema | None,
        "type": str | None,
    },
    total=False,
)


class SwaggerPathMethod(TypedDict):
    consumes: list[Literal["application/json"]]
    produces: list[Literal["application/json"]]
    description: str
    operationId: str
    parameters: list[SwaggerParameter]
    responses: dict[str, SwaggerResponse]
    summary: str
    tags: list[str]


class SwaggerDict(TypedDict):
    basePath: str
    definitions: dict["DefinitionNames", SwaggerDefinition]
    info: SwaggerInfo
    paths: dict["SwaggerPaths", dict["SwaggerPathMethods", SwaggerPathMethod]]
