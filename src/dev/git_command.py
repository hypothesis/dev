"""A wrapper around running Git commands."""

from subprocess import check_output


class Git:
    """Handy git methods."""

    # pylint: disable=too-few-public-methods

    @classmethod
    def clone(cls, git_url, target_dir):
        """Clone a project from a git URL into a directory."""

        check_output(["git", "clone", git_url, target_dir])
