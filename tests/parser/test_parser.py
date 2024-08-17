import ast
from ast import ClassDef
from unittest.mock import patch

from personal_python_minifier.parser import MinifyUnparser

from tests.utils import noop


def test_ignore_base_classes(parser: MinifyUnparser):
    class_with_bases: ClassDef = ClassDef(
        "SomeClass", bases=[ast.expr(id="ABC")], body=[]
    )
    with patch.object(ast._Unparser, "visit_ClassDef", noop):
        parser.visit_ClassDef(class_with_bases, base_classes_to_ignore=["ABC"])

    assert len(class_with_bases.bases) == 0
