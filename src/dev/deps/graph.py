"""Methods for generating graphs from dependency tree data."""

from subprocess import check_output
from tempfile import NamedTemporaryFile

from jinja2 import Template
from pkg_resources import resource_string

from dev.models.product import OUR_LIBS


class Graph:
    """Tools to create Graphviz graphs from dependency tree data."""

    @classmethod
    def create_png(cls, tree_data, output_file, algo="dot"):
        """Create a graph from the specified tree data.

        :param tree_data: Tree data produced by `dev.deps.tree.DepTree`
        :param output_file: Target file to create PNG
        :param algo: One of: `dot`, `neato`, `fdp`, `sfdp`, `circo`, `twopi`
        """
        with NamedTemporaryFile() as dot_file:
            dot_file.write(cls.create_dot(tree_data).encode("utf-8"))
            dot_file.flush()

            check_output([algo, "-Tpng", "-o", output_file, dot_file.name])

    _TEMPLATE = Template(
        resource_string("dev", "templates/dependency_graph.dot.jinja2").decode("utf-8")
    )

    @classmethod
    def create_dot(cls, tree_data):
        """Create a graph from the specified tree data.

        :param tree_data: Tree data produced by `dev.deps.tree.DepTree`
        :return: A string containing a graphviz graph
        """

        packages = tree_data["packages"]

        return cls._TEMPLATE.render(
            root=tree_data["root"],
            packages=packages,
            color_for=cls._color_for,
            max_version=cls._max_version,
        )

    @classmethod
    def _max_version(cls, package):
        if not package["python_versions"]:
            return "unknown"

        return package["python_versions"][-1]

    _VERSION_COLOR_MAP = {
        "3.9": "green",
        "3.8": "greenyellow",
        "3.7": "yellow",
        "3.6": "orange",
    }

    @classmethod
    def _color_for(cls, package):
        versions = package["python_versions"]

        if package["normalized_name"] in OUR_LIBS:
            return "darkslategray1"

        for key, color in cls._VERSION_COLOR_MAP.items():
            if key in versions:
                return color

        return "red"
