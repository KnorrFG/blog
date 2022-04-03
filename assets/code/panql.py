"""Contains functions related to pandas"""
import ast
from collections import namedtuple
from typing import Callable

import pandas as pd


class Select:
    """Transformes a pandas.DataFrame with an SQL-like statement.

    E.g.:

    ..code:: python

        Select("subscript, kappa as value")\
            .Where("(c == 1 or c == 10) and kappa > 0")(my_frame)

    """
    Var = namedtuple("Var", ["name", "alias"], defaults=(None,))

    def __call__(self, df: pd.DataFrame)-> pd.DataFrame:
        selected_frame = df[[var.name for var in self.vars]]
        return selected_frame.rename(columns={
            var.name: var.alias
            for var in self.vars if var.alias
        })

    def Where(self, expr: str)-> Callable[[pd.DataFrame], pd.DataFrame]:
        where_filter = Where(expr)

        def inner_func(df: pd.DataFrame)-> pd.DataFrame:
            return self(where_filter(df))

        return inner_func

    @staticmethod
    def _to_var(expression: str):
        return Select.Var(*expression.strip().split(" as "))

    def __init__(self, instruction: str):
        self.vars = tuple(map(Select._to_var, instruction.split(",")))


class Where:
    """Allows for nicely readable DataFrame filtering, e.g.:

        ..code:: python

            Where("c == 0.01 and val > 0")(my_frame)

    """
    class TreeRewriter(ast.NodeTransformer):
        def __init__(self, mat_name):
            super().__init__()
            self.mat_name = mat_name

        @staticmethod
        def _bool_op_replacement_type(node):
            return ast.BitAnd if isinstance(node.op, ast.And)\
                else ast.BitOr

        def _nested_bin_op(self, bop, values):
            bot_most = ast.BinOp(left=values[-1],
                                 right=values[-2],
                                 op=bop())
            current_top = bot_most
            for node in reversed(values[:-2]):
                current_top = ast.BinOp(right=node,
                                        left=current_top,
                                        op=bop)
            return current_top

        def visit_Name(self, node):
            return ast.copy_location(ast.Attribute(
                value=ast.Name(id=self.mat_name, ctx=ast.Load()),
                attr=node.id, ctx=ast.Load()), node)

        def visit_BoolOp(self, node):
            self.generic_visit(node)
            return ast.copy_location(self._nested_bin_op(
                Select.TreeRewriter._bool_op_replacement_type(node),
                node.values), node)

    def __call__(self, df: pd.DataFrame)-> pd.DataFrame:
        filter_obj = eval(self.compiled_expr)
        return df[filter_obj]

    def __init__(self, expr: str):
        filtered_tree = Where.TreeRewriter("df").visit(ast.parse(expr))
        expression = ast.Expression(body=filtered_tree.body[0].value)
        ast.fix_missing_locations(expression)
        self.compiled_expr = compile(expression, filename="<ast>", mode="eval")
