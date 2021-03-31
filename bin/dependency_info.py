"""List dependencies in order of usage and python version.

To run:

 * tox -e tests --run-command "python bin/dependency_info.py"
"""

from collections import defaultdict

from packaging.version import parse as parse_version

from dev.models.product import OUR_LIBS, Application, Library

OUTPUT_DIR = "/tmp/dep_graph"
CHECKOUT_DIR = f"{OUTPUT_DIR}/git"

# SPECIFIC_PRODUCT = Application.get('h_periodic')
SPECIFIC_PRODUCT = None


def _print_versions(by_version):
    for version, packages in sorted(by_version.items(), key=lambda item: item[0]):
        print(f"Python: {version}")
        for package in sorted(packages, key=lambda package: -package.count):
            ours = "[ours] " if package.normalized_name in OUR_LIBS else ""

            print(
                f"\t{package.count}: {ours}{package.normalized_name}\t\t{list(package.usages)}"
            )


def _summarize_requirements(products):
    usages = defaultdict(set)
    packages = {}

    # Get requirements and work out what uses them
    for product in products:
        for req in product.requirements():
            packages[req.normalized_name] = req
            usages[req.normalized_name].add(product.code)

    # Organise the requirements by the Python version they support
    by_version = defaultdict(list)
    for package in packages.values():
        version = parse_version("unknown")
        if versions := package.python_versions:
            version = versions[-1]

        package.count = len(usages[package.normalized_name])
        package.usages = usages[package.normalized_name]
        by_version[version].append(package)

    return by_version


if __name__ == "__main__":
    if SPECIFIC_PRODUCT:
        # Check out a specific product if specified
        products_to_analyze = [SPECIFIC_PRODUCT]
        SPECIFIC_PRODUCT.clone(f"{CHECKOUT_DIR}/{SPECIFIC_PRODUCT.code}")
    else:
        # Check out the various products
        products_to_analyze = list(lib for lib in Library.get_all() if lib.on_pypi)

        for app in Application.get_all():
            app.clone(f"{CHECKOUT_DIR}/{app.code}")
            products_to_analyze.append(app)

    packages_by_version = _summarize_requirements(products_to_analyze)
    _print_versions(packages_by_version)
