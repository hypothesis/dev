"""Methods for generating dependency trees."""

from dev.models.product import OUR_LIBS


class DepTree:
    """A tree of dependencies."""

    @classmethod
    def for_product(cls, product):
        """Create a tree from a Product object."""

        return cls(product, children=[DepTree(req) for req in product.requirements()])

    def __init__(self, package, children=None):
        self.package = package
        if children is None:
            children = [DepTree(req) for req in package.requirements]

        self.children = children

    def unique_children(self, seen_before=None):
        """Return the unique packages in the tree."""

        if seen_before is None:
            seen_before = set()

        for child in self.children:
            name = child.package.normalized_name
            if name in seen_before:
                continue

            seen_before.add(name)
            yield child
            yield from child.unique_children(seen_before)

    def serialize(self):
        """Represent the tree as a nested dict."""

        root = self.package.serialize()
        root["dependencies"] = {
            node.package.normalized_name: list(node.package.requirement_types)
            for node in self.children
        }

        packages = {}
        for child in self.unique_children():
            child_data = child.package.serialize()
            child_data["dependencies"] = [
                sub_child.package.normalized_name for sub_child in child.children
            ]
            packages[child.package.normalized_name] = child_data

        data = {"root": root, "packages": packages}

        return data


class TreeProcessing:
    """Tools to simplify the tree output for simpler graphs."""

    @classmethod
    def prune(
        # pylint: disable=too-many-arguments
        cls,
        tree_data,
        specified=None,
        our_lib_dependencies=True,
        our_deps_if_ok=True,
        deps_of_deps_if_ok=True,
    ):
        """Perform multiple simplications on a tree."""
        if specified:
            cls.prune_specified(tree_data, specified)
        if our_lib_dependencies:
            cls.prune_our_lib_dependencies(tree_data)
        if our_deps_if_ok:
            cls.prune_direct_deps_if_supported(tree_data)
        if deps_of_deps_if_ok:
            cls.prune_deps_of_deps_if_supported(tree_data)

        cls.prune_unreferenced_dependencies(tree_data)

    @classmethod
    def prune_specified(cls, tree_data, prune):
        """Get rid of the specified dependencies."""
        for package_data in tree_data["packages"].values():
            package_data["dependencies"] = [
                dep for dep in package_data["dependencies"] if dep not in prune
            ]

        for name in prune:
            tree_data["root"]["dependencies"].pop(name, None)

    @classmethod
    def prune_our_lib_dependencies(cls, tree_data):
        """Remove dependencies if a package is one of ours."""

        for package_name, package_data in tree_data["packages"].items():
            if package_name in OUR_LIBS:
                package_data["dependencies"] = []

    @classmethod
    def prune_direct_deps_if_supported(cls, tree_data, required_version="3.9"):
        """Remove direct dependencies that support the required version."""

        prune = []
        for name in tree_data["root"]["dependencies"].keys():
            if required_version in tree_data["packages"][name]["python_versions"]:
                prune.append(name)

        for name in prune:
            tree_data["root"]["dependencies"].pop(name)

    @classmethod
    def prune_deps_of_deps_if_supported(cls, tree_data, required_version="3.9"):
        """Don't list dependencies of things which the required version."""

        for package_data in tree_data["packages"].values():
            if required_version in package_data["python_versions"]:
                package_data["dependencies"] = []

    @classmethod
    def prune_unreferenced_dependencies(cls, tree_data):
        """Remove anything from the graph that is not referenced."""

        referenced = set(tree_data["root"]["dependencies"].keys())
        packages = set()

        for package_name, package_data in tree_data["packages"].items():
            packages.add(package_name)
            referenced.update(package_data["dependencies"])

        unreferenced = packages - referenced
        ref_by_unref = set()
        for package_name in unreferenced:
            ref_by_unref.update(tree_data["packages"][package_name]["dependencies"])
            tree_data["packages"].pop(package_name)

        if ref_by_unref:
            cls.prune_unreferenced_dependencies(tree_data)
