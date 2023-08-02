from enum import Enum


class DefinitionTypes(Enum):
    OBJECT = "object"
    ARRAY = "array"


class SwaggerPathMethods(Enum):
    GET = "get"
    POST = "post"


class SwaggerParameterTypes(Enum):
    HEADER = "header"
    QUERY = "query"
    BODY = "body"
