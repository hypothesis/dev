"""Representations of our libraries and applications."""

import json
import os
from glob import glob

from pkg_resources import resource_stream

from dev.deps.package import Package
from dev.deps.requirements_file import RequirementsFile
from dev.git_command import Git


class Product:
    """A Hypothesis product."""

    _DATA = {}

    def __init__(self, code, git_url):
        self.code = code
        self.git_url = git_url
        self._local_copy = None

    def clone(self, target_dir=None, force=False):
        """Clone the product from Git."""

        if not target_dir:
            target_dir = self._local_copy

        if not target_dir:
            raise ValueError(
                "No local copy checked out. Do you need to set target_dir?"
            )

        if not os.path.exists(target_dir) or force:
            Git.clone(self.git_url, target_dir)

        self._local_copy = target_dir
        return target_dir

    def local_path(self, *parts):
        """Get a path to a file in a local copy of the project."""
        if not self._local_copy:
            self.clone()

        return os.path.join(self._local_copy, *parts)

    def serialize(self):
        """Represent this product as a dict."""

        return {"name": self.code, "git_url": self.git_url}

    @classmethod
    def get(cls, product_code):
        """Get a product by code."""

        return cls(product_code, **cls._DATA[product_code])

    @classmethod
    def get_all(cls):
        """Iterate through all products."""

        for product_code in cls._DATA:
            yield cls.get(product_code)


class Application(Product):
    """A Hypothesis application."""

    _DATA = json.load(resource_stream("dev", "resources/products.json"))

    def requirements(self):
        """Get the requirements of the application marked with type."""

        requirements = {}

        for req_file in self._requirements_files():
            for req in req_file.requirements:
                name = req.normalized_name
                req = requirements.setdefault(name, req)
                req.requirement_types.add(req_file.type)

        return requirements.values()

    def _requirements_files(self):
        return [
            RequirementsFile(filename)
            for filename in glob(self.local_path("requirements", "*.in"))
        ]


class Library(Product):
    """A Hypothesis library."""

    _DATA = json.load(resource_stream("dev", "resources/libraries.json"))

    def __init__(self, *args, on_pypi=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_pypi = on_pypi

    def requirements(self):
        """Get the requirements of the library marked with type."""
        package = Package(self.code)

        requirements = {}

        for req_type, extra in (("dist", None), ("tests", "tests")):
            for req in package.get_requirements(extra):
                name = req.normalized_name
                req = requirements.setdefault(name, req)
                req.requirement_types.add(req_type)

        # Don't list the main dependencies again in our test deps etc.
        for req in requirements.values():
            if "dist" in req.requirement_types:
                req.requirement_types = {"dist"}

        return requirements.values()


OUR_LIBS = set(lib.code for lib in Library.get_all())
