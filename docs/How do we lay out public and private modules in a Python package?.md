# How do we lay out our Python packages?

Aims:

1. Differente public interface from internal code, because it makes maintenance easier

2. Provide a place to put internal collaborators: they can be underscored (internal) names within a class or module, or underscored module or subpackage names within a package

3. Avoid "util" or "helper" modules that tend to collect unrelated code together in one generic place, instead of keeping code close to where it's used

Approach:

1. A "package" is any directory that contains an `__init__.py` file.

2. The "public interface" of a class, module or package is all the names that're used by code outside of that class, module or package.

   * Some packages, like an `<APP>.views` package, contain code that gets called by a framework rather than by other parts of our own code. For example, Pyramid calls the view functions, predicates, etc in `<APP>.views`. **The rule applies to these packages in just the same way**: the public interface of `<APP>.views` package is all the names that're used by code outside of `<APP>.views`. The outside code in this case is Pyramid's code, not our own.

3. Names that're internal to a class, module or package begin with leading underscores, names that're part of the public interface don't.

   For packages this means that internal module's file names begin with a leading underscore: `_foo.py`, and internal sub-package's folder names begin with a leading underscore: `_bar/`.

## Exception Views Module Naming

Pyramid [exception views](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views) present a view-specific code layout issue: you'll probably want to put them in an `exceptions.py` file, but `exceptions.py` is the name that we use in all of our packages for the module that contains that package's exception classes.

**Decision**: just put both custom exception classes (if the `views` package has any) and Pyramid exception views both together in `views/exceptions.py` (no leading underscore).

## Importing names into `__init__.py` for convenience

We often import all the names (classes etc) from a package into that package's `__init__.py` file. For example `h/models/__init__.py`:

```python
from h.models.activation import Activation
from h.models.annotation import Annotation
from h.models.annotation_moderation import AnnotationModeration
...
```

We do this so that:

1. User code can just do `from h.models import Annotation, Group, User` instead of having to do `from h.models.annotation import Annotation` and `from h.models.group import Group` and `from h.models.user import User` separately

2. Internally rearranging the `h.models` package is easier: moving names between modules and subpackages won't break any calling code

## Don't underscore modules when you import their names into `__init__.py`

If all of the names from `foo/bar.py` are imported into `foo/__init__.py`, **don't** rename `foo/bar.py` to `foo/_bar.py`. Doing so would result in all `foo/*.py` filenames getting leading underscores since `foo/__init__.py` likely imports the names from all of them. The underscores would no longer help distinguish modules that contain public things and modules that only contain internal collaborators.

## We don't use `__all__`

We don't put `__all__`'s in our modules. We don't have any modules that're designed to be used via `from <module> import *`. And we haven't found any introspection benefits to `__all__`.

Instead just put leading underscores on internal names, and no leading underscores on public names.

If you ever have a need to make an underscored name public, or a non-underscored name internal, and you can't rename to add or remove the leading underscore, then use a docstring or code comment to say that the name is public or internal despite the (lack of) a leading underscore
