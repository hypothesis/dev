"""Methods for discovering information about packages."""

import json
import re
from functools import cached_property, lru_cache

import requests
from diskcache import Cache
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.version import parse as parse_version
from pkg_resources import resource_filename, resource_stream

# Info we've gathered manually
PACKAGE_INFO = json.load(resource_stream("dev", "resources/packages.json"))


def normalized_name(name):
    """Get a normalized version of a package name for comparison."""

    return name.lower().replace("-", "_").strip()


class PyPIAPI:
    """Handy access to the PyPI JSON API."""

    # pylint: disable=too-few-public-methods

    _cache = Cache(resource_filename("dev", "resources/pypi_cache"))

    """Interface to the PyPI JSON API for getting data about packages."""

    def get(self, project_name):
        """Get details of a specific package."""
        return self._get(normalized_name(project_name))

    @lru_cache(1024)
    @_cache.memoize()
    # This is quite slow without the caching above. Both in memory and disk
    # help quite a bit
    # pylint: disable=no-self-use
    # I can't get `diskcache` to work on a class method
    def _get(self, name):
        print(f"Getting details from PyPI for: {name}")
        response = requests.get(f"https://pypi.org/pypi/{name}/json")
        response.raise_for_status()

        return response.json()


class Package(Requirement):
    """A python package with handy metadata access."""

    pypi_api = PyPIAPI()

    def __init__(self, *args, **kwargs):
        self.requirement_types = set()
        super().__init__(*args, **kwargs)

        self.normalized_name = normalized_name(self.name)

        data = self.pypi_api.get(self.name)

        self.info = data["info"]
        self.releases = data["releases"]

    @cached_property
    def requirements(self):
        """Get the install requirements of this package."""
        return self.get_requirements()

    def get_requirements(self, req_type=None):
        """Get specific types of requirements (like "tests")."""
        requires = self.info["requires_dist"]

        if not requires:
            return []

        env = default_environment()
        env["extra"] = req_type

        reqs = []
        for item in requires:
            req = Package(item)
            if req.marker is None or req.marker.evaluate(env):
                reqs.append(req)

        return reqs

    _PYTHON_CODE_REGEX = re.compile(r"^cp(\d\d)$")

    @property
    def latest_release(self):
        """Get details of the latest release of this package."""

        # Something in requests or JSON parsing is discarding the order given
        # to us by PyPI. This means the versions end up sorted in lexical order
        # so  1.1, 1.10, 1.9 ...

        last_version = sorted([parse_version(ver) for ver in self.releases.keys()])[-1]

        return self.releases[str(last_version)]

    @cached_property
    def python_versions(self):
        """Get the supported python versions."""

        versions = set()

        versions.update(self.declared_versions())
        versions.update(self.implied_versions())
        versions.update(self.known_versions())

        return list(sorted(versions))

    @cached_property
    def undeclared_versions(self):
        """Get a list of inferred (but not declared) versions."""

        versions = set(self.python_versions)
        versions -= set(self.declared_versions())

        return list(sorted(versions))

    def declared_versions(self):
        """Get version information from the declared classifiers."""

        for classifier in self.info["classifiers"]:
            parts = classifier.split(" :: ")

            if len(parts) != 3:
                continue

            if parts[0] != "Programming Language" or parts[1] != "Python":
                continue

            python_version = parts[2]

            version = parse_version(python_version)

            # This will parse any old string, but only numbered versions have a
            # "release" which is a tuple like (3, 6).
            if version.release:
                yield version

    def implied_versions(self):
        """Get version information based on the compiled wheels."""

        for python_code in set(dist["python_version"] for dist in self.latest_release):
            if match := self._PYTHON_CODE_REGEX.match(python_code):
                digits = match.group(1)
                yield parse_version(f"{digits[0]}.{digits[1]}")

    def known_versions(self):
        """Get version information based on our hand curated information."""

        if info := PACKAGE_INFO.get(self.normalized_name):
            yield from (parse_version(ver) for ver in info["python_versions"].keys())

    def serialize(self):
        """Represent this package as a dict."""

        return {
            "name": self.name,
            "normalized_name": self.normalized_name,
            "python_versions": [str(v) for v in self.python_versions],
            "undeclared_versions": [str(v) for v in self.undeclared_versions],
        }
