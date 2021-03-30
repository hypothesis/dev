"""A script for generating graphs of our dependencies.

To run:

 * tox -e tests --run-command "python bin/graph_dependencies.py"
"""

from dev.deps.graph import Graph
from dev.deps.tree import DepTree, TreeProcessing
from dev.models.product import Application, Library

OUTPUT_DIR = "/tmp/dep_graph"
CHECKOUT_DIR = f"{OUTPUT_DIR}/git"
IGNORE_LIBS = {"setuptools", "six"}


def _graph_app(application):
    print(f"\nGraphing {application.code}")
    print("\tCloning...")
    application.clone(f"{CHECKOUT_DIR}/{application.code}")

    print("\tGenerating data")
    tree_data = DepTree.for_product(application).serialize()
    TreeProcessing.prune(tree_data, specified=IGNORE_LIBS)

    print("\tGraphing")
    Graph.create_png(tree_data, f"{OUTPUT_DIR}/app_{application.code}.png", algo="dot")


def _graph_lib(library):
    print(f"\nGraphing {library.code}")
    if not library.on_pypi:
        print("\tCan't handle local libs yet...")
        return

        # print("\tCloning...")
        # lib.clone(f"{CHECKOUT_DIR}/{lib.code}")

    print("\tGenerating data")
    tree_data = DepTree.for_product(library).serialize()
    TreeProcessing.prune(
        tree_data,
        specified=IGNORE_LIBS,
        our_lib_dependencies=False,
        our_deps_if_ok=False,
        deps_of_deps_if_ok=True,
    )

    print("\tGraphing")
    Graph.create_png(tree_data, f"{OUTPUT_DIR}/lib_{library.code}.png", algo="dot")


if __name__ == "__main__":
    for lib in Library.get_all():
        _graph_lib(lib)

    for app in Application.get_all():
        _graph_app(app)

    print(f"\nGenerated graphs in {OUTPUT_DIR}")
