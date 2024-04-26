from pathlib import Path

import proto_schema_parser.parser as proto_parser
from proto_schema_parser.ast import Enum, EnumValue


class ProtoReader:
    def __init__(self, proto_path: str | Path):
        """Create a new ProtoReader instance.

        Args:
            workspace (Path): The path of the workspace.
            proto_path (str | Path): The path to the proto files.
        """
        self.proto_code_dict = {}

        for proto_file_path in Path(proto_path).glob("**/*.proto"):
            with open(proto_file_path, encoding="utf-8") as proto_file:
                self.proto_code_dict[proto_file.name] = proto_file.read()

    def read(self) -> dict[str, dict[str, str]]:
        """Read in values from proto code.

        Returns:
            dict[str, dict[str,str]]: Parsed proto values.
        """
        proto: dict[str, dict[str, str]] = {}
        for _, proto_code in self.proto_code_dict.items():
            proto = self._read_enums(proto_code) | proto
        return proto

    def _read_enums(self, proto_code: str) -> dict[str, dict[str, str]]:
        """Reads enums from proto code.

        Args:
            proto_code (str): Proto code as a string.

        Returns:
            dict[str, dict[str,str]]: Parsed enums as a dictionary.
        """
        if "enum " not in proto_code:
            return {}

        proto_ast = proto_parser.Parser().parse(proto_code)
        enums = {}
        for enum_element in filter(
            lambda x: isinstance(x, Enum), proto_ast.file_elements
        ):
            enum_values = {}
            for enum_value in filter(
                lambda x: isinstance(x, EnumValue), enum_element.elements
            ):
                enum_values[enum_value.name] = enum_value.number
            enums[enum_element.name] = enum_values

        return enums
