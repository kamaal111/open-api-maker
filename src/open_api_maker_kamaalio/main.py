import sys
import yaml
from getopt import getopt
from typing import TYPE_CHECKING, Any
from pathlib import Path

if TYPE_CHECKING:
    from .swagger_types import (
        SwaggerDict,
        SwaggerPathMethod,
        SwaggerResponse,
        SwaggerDefinition,
        SwaggerParameter,
    )
    from .enums import SwaggerPathMethods


def make_array_schema_name(name: str):
    return f"{name}s"


def get_original_array_schema_name(name: str):
    return name[:-1]


def get_swagger_data(input_file_text: str) -> "SwaggerDict":
    swagger_dict = yaml.load(input_file_text, Loader=yaml.CLoader)
    return swagger_dict


def make_schema_name(name: str):
    formatted_name = name.split("/")[-1].split(".")[-1]
    capitilized_name = f"{formatted_name[0].upper()}{formatted_name[1:]}"
    return capitilized_name


def omit_empty(data: dict[str, Any]):
    omitted_data = {}
    for key, value in data.items():
        if value:
            omitted_data[key] = value
    return omitted_data


def omit(data: dict[str, Any], key: str):
    omitted_data = {}
    for data_key, value in data.items():
        if key != data_key:
            omitted_data[data_key] = value
    return omitted_data


def map_swagger_path_responses_for_xcode(
    responses: dict[str, "SwaggerResponse"], produces: list[str]
):
    mapped_responses = {}
    for response_key, response_value in responses.items():
        mapped_content = {}
        for content_type in produces:
            schema = response_value["schema"]
            formatted_schema = {
                "$ref": f"#/components/schemas/{make_schema_name(schema.get('$ref') or schema['items']['$ref'])}",
                "type": schema.get("type"),
            }
            if formatted_schema["type"] == "array":
                formatted_schema["$ref"] = make_array_schema_name(
                    formatted_schema["$ref"]
                )

            mapped_content[content_type] = {"schema": omit_empty(formatted_schema)}

        mapped_responses[response_key] = {
            "description": response_value["description"],
            "content": mapped_content,
        }

    return mapped_responses


def map_swagger_parameters_for_xcode(parameters: list["SwaggerParameter"] | None):
    if not parameters:
        return None

    mapped_parameters = []
    for parameter in parameters:
        mapped_parameter = {}
        if parameter["in"] == "body":
            continue

        for key, value in parameter.items():
            if key == "default":
                continue

            if key == "type":
                mapped_parameter["schema"] = {key: value}
            else:
                mapped_parameter[key] = value

        mapped_parameters.append(mapped_parameter)

    return mapped_parameters


def map_swagger_path_request_body(
    parameters: list["SwaggerParameter"] | None, consumes: list[str]
):
    if not parameters:
        return None

    for parameter in parameters:
        if parameter["in"] == "body":
            mapped_content = {}
            for consume_type in consumes:
                mapped_content[consume_type] = {
                    "schema": {
                        "$ref": f"#/components/schemas/{make_schema_name(parameter['schema']['$ref'])}"
                    }
                }

            return {
                "description": parameter["description"],
                "required": parameter["required"],
                "content": mapped_content,
            }


def map_swagger_paths_for_xcode(
    paths: dict[str, dict["SwaggerPathMethods", "SwaggerPathMethod"]]
):
    mapped_paths = {}
    for path, data in paths.items():
        mapped_path_data = {}
        for key, value in data.items():
            mapped_path_data[key] = omit_empty(
                {
                    "description": value["description"],
                    "operationId": value["operationId"],
                    "responses": map_swagger_path_responses_for_xcode(
                        responses=value["responses"], produces=value["produces"]
                    ),
                    "summary": value["summary"],
                    "tags": value["tags"],
                    "parameters": map_swagger_parameters_for_xcode(
                        value.get("parameters")
                    ),
                    "requestBody": map_swagger_path_request_body(
                        parameters=value.get("parameters"), consumes=value["consumes"]
                    ),
                }
            )
        mapped_paths[path] = mapped_path_data

    return mapped_paths


def map_swagger_definitions_for_xcode(
    definitions: dict[str, "SwaggerDefinition"], array_responses=list[str]
):
    mapped_definitations = {}
    for name, definition in definitions.items():
        formatted_name = make_schema_name(name)
        mapped_definitations[formatted_name] = definition
        if formatted_name in array_responses:
            mapped_definitations[make_array_schema_name(formatted_name)] = {
                "schema": {
                    "$ref": f"#/components/schemas/{formatted_name}",
                    "type": "array",
                }
            }

    return mapped_definitations


def extract_array_responses(mapped_paths: dict):
    array_responses = []
    for path in mapped_paths.values():
        for method in path.values():
            for response in method["responses"].values():
                content = response["content"]
                for content_type in content.keys():
                    response_schema = content[content_type]["schema"]
                    if response_schema.get("type") == "array":
                        response_schema_name = response_schema["$ref"]
                        array_responses.append(
                            get_original_array_schema_name(
                                response_schema_name.split("/")[-1]
                            )
                        )

    return array_responses


def remove_types_from_path_schemas(data: dict):
    mapped_paths = {}
    for path_key, path in data["paths"].items():
        mapped_path = path.copy()
        for method_key, method in path.items():
            mapped_method = method.copy()
            for response_key, response in method["responses"].items():
                mapped_response = response.copy()
                for content_type in response["content"].keys():
                    if response["content"][content_type]["schema"].get("type"):
                        del mapped_response["content"][content_type]["schema"]["type"]

                mapped_method["responses"][response_key] = mapped_response

            mapped_path[method_key] = mapped_method

        mapped_paths[path_key] = mapped_path

    mapped_data = data.copy()
    mapped_data["paths"] = mapped_paths
    return mapped_data


def map_swagger_data_for_xcode(swagger_dict: "SwaggerDict"):
    mapped_paths = map_swagger_paths_for_xcode(swagger_dict["paths"])

    return yaml.dump(
        remove_types_from_path_schemas(
            {
                "openapi": "3.0.3",
                "info": swagger_dict["info"],
                "paths": mapped_paths,
                "components": {
                    "schemas": map_swagger_definitions_for_xcode(
                        definitions=swagger_dict["definitions"],
                        array_responses=extract_array_responses(
                            mapped_paths=mapped_paths
                        ),
                    )
                },
            }
        )
    )


def write_api_spec(spec: str, output_path: str):
    destination_file = Path(output_path)
    destination_file.write_text(spec)


def parse_opts(shortopts: list[str] = [], longopts: list[str] = []) -> dict[str, str]:
    argv = sys.argv[1:]
    unique_shortopts = set(shortopts)
    unique_longopts = set(longopts)
    given_opts = unique_shortopts.union(unique_longopts)
    opts, _ = getopt(
        argv, ":".join(unique_shortopts) + ":", map(lambda x: f"{x}=", unique_longopts)
    )
    opts_dict = {}
    for opt, arg in opts:
        if arg == "":
            continue

        for given_opt in given_opts:
            opt = opt.replace("-", "", 2)
            if opt != given_opt:
                continue

            opts_dict[given_opt] = arg
            break

    return opts_dict
