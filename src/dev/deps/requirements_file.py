"""Methods for parsing Python requirements files."""

import os
from functools import cached_property

from dev.deps.package import Package


class RequirementsFile:
    """A requirements file in a project."""

    # pylint: disable=too-few-public-methods

    def __init__(self, filename):
        self.filename = filename
        self.type = os.path.basename(filename).replace(".in", "")

    @cached_property
    def requirements(self):
        """Yield all requirements as Package objects."""

        requirements = []

        with open(self.filename) as handle:
            for line in handle:
                line = line.strip()
                if line.startswith("#") or line.startswith("-r") or not line:
                    continue

                if "#" in line:
                    line = line[: line.index("#")]

                requirements.append(Package(line))

        return requirements
