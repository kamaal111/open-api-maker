from src.open_api_maker_kamaalio.main import (
    get_original_array_schema_name,
    get_swagger_data,
    make_array_schema_name,
)


def test_make_array_schema_name():
    assert make_array_schema_name("kamaal") == "kamaals"


def test_get_original_array_schema_name():
    assert get_original_array_schema_name("kamaals") == "kamaal"


def test_get_swagger_data():
    swagger_text = """
    basePath: /api/v1
    """
    assert get_swagger_data(swagger_text) == {"basePath": "/api/v1"}
