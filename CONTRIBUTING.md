# Contributing to `datadivr`

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

You can contribute in many ways:

# Types of Contributions

## Report Bugs

Report bugs at https://github.com/menchelab/datadivr/issues

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

## Fix Bugs

Look through the GitHub issues for bugs.
Anything tagged with "bug" and "help wanted" is open to whoever wants to implement a fix for it.

## Implement Features

Look through the GitHub issues for features.
Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

## Write Documentation

datadivr could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

## Submit Feedback

The best way to send feedback is to file an issue at https://github.com/menchelab/datadivr/issues.

If you are proposing a new feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

# Get Started!

Ready to contribute? Here's how to set up `datadivr` for local development.
Please note this documentation assumes you already have `uv` and `Git` installed and ready to go.

1\. Fork the `datadivr` repo on GitHub.

2\. Clone your fork locally:

```bash
cd <directory_in_which_repo_should_be_created>
git clone git@github.com:menchelab/datadivr.git
```

3\. Now we need to install the environment. Navigate into the directory

```bash
cd datadivr
```

Then, install and activate the environment with:

```bash
uv sync
```

4\. Install pre-commit to run linters/formatters at commit time:

```bash
uv run pre-commit install
```

5\. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

6\. Alternatively you can use vscode devcontainer feature which only requires you to have vscode and docker desktop installed, when you open the project in vscode install the extension and click the reopen in container button

Now you can make your changes locally.

6\. Don't forget to add test cases for your added functionality to the `tests` directory.

7\. When you're done making changes, check that your changes pass the formatting tests.

```bash
make check
```

Now, validate that all unit tests are passing:

```bash
make test
```

9\. Before raising a pull request you should also run tox.
This will run the tests across different versions of Python:

```bash
uv run tox
```

10\. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

When writing commit messages, please follow the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/). This helps maintain a standardized commit history and enables automated tooling. The basic format is:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types include:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `chore`: Changes to build process or auxiliary tools

Example commit messages:

```
feat(api): add new data validation endpoint
fix: correct memory leak in processing loop
docs: update installation instructions
```

11\. Submit a pull request through the GitHub website.

# Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1\. The pull request should include tests.

2\. If the pull request adds functionality, the docs should be updated.
Put your new functionality into a function with a docstring.
