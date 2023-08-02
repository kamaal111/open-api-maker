from pathlib import Path

from .main import (
    get_swagger_data,
    map_swagger_data_for_xcode,
    parse_opts,
    write_api_spec,
)


def cli():
    opts = parse_opts(longopts=["input", "output"])
    input_path = opts.get("input")
    if not input_path:
        raise Exception("No --input provided")

    output_path = opts.get("output")
    if not output_path:
        raise Exception("No --output provided")

    swagger_file = Path(input_path)
    swagger_data = get_swagger_data(swagger_file.read_text())
    mapped_swagger_data = map_swagger_data_for_xcode(swagger_data)
    write_api_spec(mapped_swagger_data, output_path)
