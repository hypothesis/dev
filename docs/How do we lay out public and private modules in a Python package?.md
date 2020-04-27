# How do we lay out public and internal modules in a Python package?

See also:

* [Organization of views package is poor](https://github.com/hypothesis/lms/issues/1245), the original issue that led to this file

We have a very simple approach:

1. A "package" is any directory that contains an `__init__.py` file

2. The "public interface" of a class, module or package is all the names that're used by code outside of that class module or package

   The calling code can be other code within the same app or it can be a third-party framework. For example Pyramid calls our view functions, so the view functions are part of the `<APP>.views` package's public interface.

3. Names that are part of the public interface of a class, module or package don't have leading underscores. Internal names that are not part of a class, module or package's public interface **do** have leading underscores.

   For example:

   1. **Classes:** public attributes and methods of a class don't have leading underscores. Internal attributes and methods within a class do have leading underscores.
   2. **Modules:** public classes, functions and other top-level names within a module don't have leading underscores. Internal attributes, methods and names within a module do have leading underscores.
   3. **Packages:** public modules within a package don't have leading underscores on their filenames, e.g. `foo.py`. Internal modules within a package do have leading underscores, e.g. `_foo.py`. Similarly public subpackages have no leading underscore (`bar/`), internal subpackages do have a leading underscore (`_bar/`).

## Aims

The above approach:

* Differentiates the public interface (that's meant to be called from outside of the package) from internal code.

  Being able to easily see what is public and what is internal encourages better code design and makes the code easier to maintain. You can more easily see what a package is "about" if you can see its public interface and ignore internal code until you need to work on it. If you can see that something is internal, you know that it's not going to be used outside of its package. If you've changed a package's internal code but haven't changed its public interface, you know that you won't have broken any code outside of the package.

* Provides a place to put internal close collaborators.

  Not everything in the `<APP>.views` package is a view, not everything in the `<APP>.models` package is a model, etc. Sometimes the views/models/whatever need to call internal collaborator classes or functions to get their jobs done. We need a place to put these internal collaborators that's localised within the package or subpackage they belong to.

* Avoids "util" or "helper" modules.

  In the past we've used an `<APP>.util` package to contain "utilities" that don't seem to belong anywhere else. This is a terrible pattern because `<APP>.util` becomes an ill-defined grab-bag of all sorts of random stuff, and because anything in `<APP>.util` looks like it might be used anywhere in the code whereas in fact it's likely only used in one place: localization breaks down. We don't want any more `<APP>.util` packages.

  Also in the past we've created local `helpers.py` modules or `helpers/` packages within packages to contain the utils or helpers just for that package. This isn't a good pattern either: it still ends up moving close collaborators away from the code that uses them, splitting functions that should live together in one module into separate modules by forcing the helper into `helpers.py`, or splitting modules that should live side-by-side in one package into separate packages by forcing the helper into a `helpers/` subpackage. It's also just annoying to always have to move everything into "helpers" modules.

## Types of Package in an App

Generally there are three different types of package within an app:

1. Packages that contain code that gets imported and called by other packages within the same app (for example: `<APP>.models`). Here it's simple: the public interface of the package is all the names that get imported and used by code outside of that package

2. Packages that contain code that gets called by a framework, usually Pyramid (for example: `<APP>.views`). Here it's a bit trickier: we define the public interface as all the things that get called _by Pyramid_. For example:

   * View classes and view methods are public interface: Pyramid calls our views to get responses to requests
     * Exception views are also public interface: Pyramid calls these too
   * Custom view predicates (which get used in Pyramid `@view_config`'s) are public interface: Pyramid calls our view predicates to determine whether to call the view or not
   * Helper functions that the views call are not public interface: these are only called by other code within the same package. They're not directly called by Pyramid

   So in the case of an `<APP>.views` package the leading underscores differentiate the views and other things that're registered with Pyramid, from internal helpers. The differentiation helps you to see what views, predicates, etc the app has without being distracted by all their collaborators.

3. Some packages will be a bit of both (1) and (2)

## Exception Views Module Naming

Pyramid [exception views](https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/views.html#custom-exception-views) present a view-specific code layout issue: you'll probably want to put them in an `exceptions.py` file, but `exceptions.py` is the name that we use in all of our packages for the module that contains that package's exception classes. 

**Decision**: just put both custom exception classes (if the `views` package has any) and Pyramid exception views both together in `views/exceptions.py` (no leading underscore)

## In-module collaborators

Although you can put collaborators in their own `_bar.py` module alongside the module(s) that call them, if some collaborators are only used within one module it's also fine to just put them in that module:

```python
# views/foo.py

from pyramid.view import view_config

@view_config(...)
def foo(request):
    # Uses _FooCollaborator.
    ...

class _FooCollaborator:
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
