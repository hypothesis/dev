# How do we lay out public and internal modules in a Python package?

See also:

* [Organization of views package is poor](https://github.com/hypothesis/lms/issues/1245), the original issue that led to this file

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)'s guidelines on [public and internal interfaces](https://www.python.org/dev/peps/pep-0008/#public-and-internal-interfaces), which say:

> Even with `__all__` set appropriately, internal interfaces (packages, modules, classes, functions, attributes or other names) should still be prefixed with a single leading underscore.
> 
> An interface is also considered internal if any containing namespace (package, module or class) is considered internal.

(A leading underscore is Python's "weak internal use indicator" both for files and directories, and for names within files.)

Let's take a Pyramid app's `views` package as an example, although this should apply equally well to any package:

* A `views` package arguably doesn't really have a "public interface": it doesn't contain any code that's meant to be imported and used by other parts of our code. But the views in a `views` package are called by Pyramid so we consider those (and other `views`-package objects that are for Pyramid to call) to be the `views` package's public interface. The same thinking also applies to other packages that just contain things for Pyramid to call

* So files in a `views` package that contain views are considered public and **don't have a leading underscore**. E.g. the foo views would be `views/foo.py`

* Collaborators for the views are only meant to be called by the views themselves and so are internal. These **do have a leading underscore**. E.g. the bar helpers would be `views/_bar.py`

* This use of leading underscores makes it easy to tell which files contain views, and which just contain internal collaborators for the views. Or in a `services` package it would make it easy to tell which files contain services, and which just contain internal collaborators for the services. In a package that contains objects that are actually supposed to be imported and used by our own code (not just called by Pyramid) the leading underscores also denote which modules contain things that are meant to be imported elsewhere in the code and which are for internal use only

* Pyramid [exception views](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views) present a view-specific code layout issue: you'll probably want to put them in an `exceptions.py` file, but `exceptions.py` is the name that we use in all of our packages for the module that contains that package's exception classes. Decision: just put both custom exception classes (if the `views` package has any) and Pyramid exception views both together in `views/exceptions.py` (no leading underscore)

## In-module collaborators

Although you can put collaborators in their own `_bar.py` module alongside the module(s) that call them, if some collaborators are only used within one module it's also fine to just put them in that module:

```python
# views/foo.py

from pyramid.view import view_config

@view_config(...)
def foo(request):
    # Uses _FooHelper.
    ...

class _FooHelper:
    ...
```

With a close-collaborator like this the unit tests would normally work by calling the `foo()` view and only testing `_FooHelper` indirectly via the `foo()` view. A close collaborator like `_FooHelper` wouldn't normally be patched in the unit tests for the `foo()` view.

Reasons **not** to do put a collaborator in-module:

* If `_FooHelper` is called by anything outside of `views/foo.py`
* If it would make either `views/foo.py` or its unit tests too long (lots of small collaborating files, rather than a few big ones, please)

## Importing names into an `__init__.py` file

We often import all the names (classes etc) from a module into that module's `__init__.py` file. For example `h/models/__init__.py`:

```python
from h.models.activation import Activation
from h.models.annotation import Annotation
from h.models.annotation_moderation import AnnotationModeration
...
```

This is done for convenience:

1. User code can just do `from h.models import Annotation, Group, User` instead of having to do `from h.models.annotation import Annotation` and `from h.models.group import Group` and `from h.models.user import User`

2. It makes it easier when you want to reorganize the code within the `h.models` package. For example renaming a module, splitting a large module into two smaller ones, or joining two modules into one. Code that does `from h.models import Annotation, Group, User` won't be broken by the reorganization

### This doesn't mean every module is internal

You might think that, since `Annotation`, `Group` and `User` are meant to be imported from `models/__init__.py` rather than from `models/annotation.py`, `models/group.py` and `models/user.py`, that `models/annotation.py`, `models/group.py` and `models/user.py` are actually internal and should have leading underscores. Don't think this, though, because it would mean that:

1. Every module in every package would have a leading underscore
2. The leading underscores would no longer be helping us to distinguish between modules that contain public things and modules that only contain internal collaborators

## We don't use `__all__`

PEP 8 [says](https://www.python.org/dev/peps/pep-0008/#public-and-internal-interfaces):

> To better support introspection, modules should explicitly declare the names in their public API using the `__all__` attribute.

We don't put `__all__`'s in our modules because we haven't found it to be useful. For example we don't have any modules that're designed to be used via `from <module> import *` (an `__all__` controls what names `import *` imports from a module). And we haven't found any introspection benefits to `__all__`.

Instead we just put leading underscores on internal names, and no leading underscores on public names.

If you ever have a need to make an underscored name public, or a non-underscored name internal, and you can't rename to add or remove the leading underscore, then use a docstring or code comment to say that the name is public or internal despite the (lack of) a leading underscore
