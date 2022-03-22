# Contributing to dupeGuru

The following is a set of guidelines and information for contributing to dupeGuru.

#### Table of Contents

[Things to Know Before Starting](#things-to-know-before-starting)

[Ways to Contribute](#ways-to-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Localization](#localization)
  * [Code Contribution](#code-contribution)
  * [Pull Requests](#pull-requests)

[Style Guides](#style-guides)
  * [Git Commit Messages](#git-commit-messages)
  * [Python Style Guide](#python-style-guide)
  * [Documentation Style Guide](#documentation-style-guide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Things to Know Before Starting
**TODO**
## Ways to contribute
### Reporting Bugs
**TODO**
### Suggesting Enhancements
**TODO**
### Localization
**TODO**
### Code Contribution
**TODO**
### Pull Requests
Please follow these steps to have your contribution considered by the maintainers:

1. Keep Pull Request specific to one feature or bug.
2. Follow the [style guides](#style-guides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing <details><summary>What if the status checks are failing?</summary>If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.</details>

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Style Guides
### Git Commit Messages
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Style Guide
- All files are formatted with [Black](https://github.com/psf/black)
- Follow [PEP 8](https://peps.python.org/pep-0008/) as much as practical
- Pass [flake8](https://flake8.pycqa.org/en/latest/) linting
- Include [PEP 484](https://peps.python.org/pep-0484/) type hints (new code)

### Documentation Style Guide
**TODO**

## Additional Notes
### Issue and Pull Request Labels
This section lists and describes the various labels used with issues and pull requests.  Each of the labels is listed with a search link as well.

#### Issue Type and Status
| Label name | Search | Description |
|------------|--------|-------------|
| `enhancement` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aenhancement) | Feature requests and enhancements. |
| `bug` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Abug) | Bug reports. |
| `duplicate` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aduplicate) | Issue is a duplicate of existing issue. |
| `needs-reproduction` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aneeds-reproduction) | A bug that has not been able to be reproduced. |
| `needs-information` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aneeds-information) | More information needs to be collected about these problems or feature requests (e.g. steps to reproduce). |
| `blocked` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Ablocked) | Issue blocked by other issues. |
| `beginner` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Abeginner) | Less complex issues for users who want to start contributing. |

#### Category Labels
| Label name | Search | Description |
|------------|--------|-------------|
| `3rd party` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3A%223rd%20party%22)  | Related to a 3rd party dependency. |
| `crash` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Acrash) | Related to crashes (complete, or unhandled). |
| `documentation` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Adocumentation) | Related to any documentation. |
| `linux` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3linux) | Related to running on Linux. |
| `mac` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Amac) | Related to running on macOS. |
| `performance` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aperformance) | Related to the performance. |
| `ui` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Aui)| Related to the visual design. |
| `windows` | [search](https://github.com/arsenetar/dupeguru/issues?q=is%3Aopen+is%3Aissue+label%3Awindows) | Related to running on Windows. |

#### Pull Request Labels
None at this time, if the volume of Pull Requests increase labels may be added to manage.
