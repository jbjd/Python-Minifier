import ast
from typing import Iterable, Literal
import warnings


from personal_python_minifier.parser.minifier import MinifyUnparser
from personal_python_minifier.parser.utils import (
    CodeToSkip,
    get_node_id_or_attr,
    ignore_base_classes,
    is_name_equals_main_node,
)


class ExcludeUnparser(MinifyUnparser):

    __slots__ = (
        "skip_name_equals_main",
        "classes_to_skip",
        "dict_keys_to_skip",
        "from_imports_to_skip",
        "functions_to_skip",
        "vars_to_skip",
    )

    # TODO: Make some kind of input class
    def __init__(
        self,
        module_name: str = "",
        target_python_version: tuple[int, int] | None = None,
        skip_asserts: bool = False,
        skip_name_equals_main: bool = False,
        from_imports_to_skip: set[str] | None = None,
        functions_to_skip: set[str] | None = None,
        vars_to_skip: set[str] | None = None,
        classes_to_skip: set[str] | None = None,
        dict_keys_to_skip: set[str] | None = None,
    ) -> None:
        super().__init__(module_name, target_python_version)

        if skip_asserts:
            self.visit_Assert = lambda _: self.visit_Pass()  # type: ignore

        self.skip_name_equals_main: bool = skip_name_equals_main

        # TODO: Test the exclusions
        self.classes_to_skip: CodeToSkip = CodeToSkip(classes_to_skip, "class")
        self.dict_keys_to_skip: CodeToSkip = CodeToSkip(dict_keys_to_skip, "dict_key")
        self.from_imports_to_skip: CodeToSkip = CodeToSkip(
            from_imports_to_skip, "from import"
        )
        self.functions_to_skip: CodeToSkip = CodeToSkip(functions_to_skip, "function")
        self.vars_to_skip: CodeToSkip = CodeToSkip(vars_to_skip, "var")

    def visit(self, node) -> str:
        result: str = super().visit(node)

        for code_excluder in [
            self.functions_to_skip,
            self.vars_to_skip,
            self.classes_to_skip,
            self.dict_keys_to_skip,
        ]:
            not_found_tokens: set[str] = code_excluder.get_not_found_tokens()
            if not_found_tokens:
                warnings.warn(
                    (
                        f"{self.module_name}: requested to skip "
                        f"{code_excluder.token_type} {', '.join(not_found_tokens)}"
                        " but was not found"
                    )
                )

        return result

    def visit_Dict(self, node: ast.Dict) -> None:
        if self.dict_keys_to_skip:
            new_dict = {
                k: v
                for k, v in zip(node.keys, node.values)
                if getattr(k, "value", "") not in self.dict_keys_to_skip
            }
            node.keys = list(new_dict.keys())
            node.values = list(new_dict.values())
        super().visit_Dict(node)

    def visit_If(self, node: ast.If) -> None:
        if self.skip_name_equals_main and is_name_equals_main_node(node.test):
            if node.orelse:
                self.traverse(node.orelse)
            return

        super().visit_If(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Skip unnecessary futures imports"""
        if not self.from_imports_to_skip.empty():
            node.names = [
                alias
                for alias in node.names
                if alias.name not in self.from_imports_to_skip
            ]

        super().visit_ImportFrom(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Only writes type annotations if necessary"""
        var_name: str = get_node_id_or_attr(node.target)
        if var_name in self.vars_to_skip:
            return

        super().visit_AnnAssign(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if (
            isinstance(node.value, ast.Call)
            and get_node_id_or_attr(node.value.func) in self.functions_to_skip
        ):
            self.visit_Pass()
            return

        # TODO: Currently if a.b.c.d only "c" and "d" are checked
        var_name: str = get_node_id_or_attr(node.targets[0])
        parent_var_name: str = get_node_id_or_attr(
            getattr(node.targets[0], "value", object)
        )
        if var_name in self.vars_to_skip or parent_var_name in self.vars_to_skip:
            return

        super().visit_Assign(node)

    def visit_ClassDef(
        self, node: ast.ClassDef, base_classes_to_ignore: Iterable[str] | None = None
    ) -> None:
        if node.name in self.classes_to_skip:
            return

        if base_classes_to_ignore:
            ignore_base_classes(node, base_classes_to_ignore)

        super().visit_ClassDef(node)

    def visit_Call(self, node: ast.Call) -> None:
        function_name: str = get_node_id_or_attr(node.func)
        if function_name in self.functions_to_skip:
            self.visit_Pass()
        else:
            super().visit_Call(node)

    def _function_helper(
        self, node: ast.FunctionDef, fill_suffix: Literal["def", "async def"]
    ) -> None:
        if node.name in self.functions_to_skip:
            return

        super()._function_helper(node, fill_suffix)
