from pathlib import Path
from typing import Optional

import proto_schema_parser.parser as proto_parser
from proto_schema_parser.ast import Enum, EnumValue


class ProtoReader:
    def __init__(self, workspace: Path, proto_path_str: Optional[str] = ""):
        """Create a new ProtoReader instance.

        Args:
            workspace (Path): The path of the workspace
            proto_path_str (str, optional): The path of the proto files.
        """
        self.proto_code_dict = {}
        if proto_path_str:
            proto_path = workspace / proto_path_str
            for proto_file_path in proto_path.glob("**/*.proto"):
                with open(proto_file_path, "r", encoding="utf-8") as proto_file:
                    self.proto_code_dict[proto_file.name] = proto_file.read()

    def read(self) -> dict[str, dict[str, str]]:
        """Read in values from proto code.

        returns dict(str, dict[str,str]): Parsed proto values.
        """
        proto: dict[str, dict[str, str]] = {}
        for _, proto_code in self.proto_code_dict.items():
            proto = self._read_enums(proto_code) | proto
        return proto

    def _read_enums(self, proto_code: str) -> dict[str, dict[str, str]]:
        """Reads enums from proto code.

        Args:
            proto_code (str): Proto code string.

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
            enums[enum_element.name] = {
                enum_value.name: enum_value.number
                for enum_value in enum_element.elements
                if isinstance(enum_value, EnumValue)
            }

        return enums
