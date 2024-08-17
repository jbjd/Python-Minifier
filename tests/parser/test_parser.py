import ast
from ast import ClassDef

from personal_python_minifier.parser import MinifyUnparser


def test_ignore_base_classes(parser: MinifyUnparser):
    class_with_bases: ClassDef = ClassDef(
        "SomeClass", bases=[ast.expr(id="ABC")], body=[], decorator_list=[], keywords=[]
    )
    parser.visit_ClassDef(class_with_bases, base_classes_to_ignore=["ABC"])

    assert len(class_with_bases.bases) == 0
