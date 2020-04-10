# Hypothesis Developer Docs & Tools

This repo is a place to put developer docs (coding guidelines and best practices etc) and tools (scripts for automating development tasks etc).

## Why another place for docs?

We wanted a quick and easy place to collaborate on documentation about our code design and architecture, and:

* We wanted it to be public, which rules out [Stack Overflow for Teams](https://stackoverflow.com/c/hypothesis/questions)

* We didn't want these docs to be lost within a sea of other stuff. That rules out GitHub Issues or other places that already have a lot of content in them

* We wanted to be able to send new architecture decisions as **pull requests** so they can be discussed and reviewed before merging. That rules out Stack Overflow for Teams, Google Drive, GitHub Issues, a GitHub repo's wiki, or anything that's not files within a GitHub repo itself

* We wanted contributing to be as quick and easy as possible. Just edit simple Markdown files in your browser using GitHub's web interface (you can use the web interface to either commit directly to master or create a new branch and start a PR). That rules out reStructuredText and Sphinx-based docs like those at https://h.readthedocs.io/ and <https://h.readthedocs.io/projects/client/>, they're simply not convenient enough to contribute to

* We wanted a place for docs and tools that apply to all projects. That rules out using a directory within any existing project repo such as the <https://github.com/hypothesis/h> repo. While some of these docs might refer to particular Hypothesis projects, not all of these docs are going to be specific to any one project. Also, committing changes to a project's master branch would kick off a build of that project and deploy to QA, and we don't want dev docs changes to trigger that.

* This repo is named "dev" rather than "docs" because it's not just for docs (it also contains scripts and tools) and to distinguish it from public facing documentation like what's at https://h.readthedocs.io/ and https://h.readthedocs.io/projects/client/. This is developer documentation. We might one day create a "docs" repo for non-project specific, public facing docs
