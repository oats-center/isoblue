# Contributing
This document describes how to go about contributing to the ISOBlue-Avena repository as well as defining how we manage pull requests, releases, and other collaborative features


## General Guidelines
If you are looking to help us, please visit our [issue tracker](https://github.com/OATS-Group/isoblue-avena/issues). If you would like to suggest or discuss a feature/bug, please email our [mailing list](https://groups.google.com/g/isoblue). Please ensure you mention the 'Avena' version of ISOBlue.


## Release Branches and Versioning
The master branch will track the current unstable version of the codebase (equivalent to the `dev` branch in many other repositories). Stable versions will be maintained using branches in the form of `release/xx.yy.zz`, similar to the [Gitlab Flow](https://docs.gitlab.com/ee/topics/gitlab_flow.html) style. This is primarily for the ability to cherry-pick bug fixes into previous releases. 

Releases will be numbered in the [Semantic Versioning](https://semver.org/) style. Version `XX.YY.ZZ` is major version `XX`, minor version `YY`, and bugfix `ZZ`. Major versions incorporate breaking changes, minor versions introduce new features, and bugfixes... fix bugs


## Feature Branches and Pull Requests
Members of the ISOBlue-Avena repository will use feature/bugfix branches in the form of `feature/feature-name` or `bugfix/bug-name`. Outside contributors forking the repository are encouraged to do the same


Once a feature/bugfix branch as reached maturity and has been properly [tested](#Testing) a pull request will be created requesting to merge the branch into master. Members of the ISOBlue-Avena repository will review the code and changes may be be requested. Given all requested changes are addressed and all tests pass, a member of the repository will approve the changes and the branch will be merged into master. If the person opening the pull request has permission to merge, it will be their responsibility to merge the branch and resolve any conflicts, otherwise one of the repository maintainers will be assigned during triage.


## Testing
As of writing, testing is currently very fluid. All outside contributors are expected to test their contributions properly before opening a pull request. Once a pull request is opened, our github actions (once completed) will preform supplemental testing. These tests must pass before a pull request will be considered. The master branch (depending on the scope of the changes, occasionally feature branches as well) will be tested on farm equipment within the Purdue OATS Research group. Once the software preforms sufficiently well in the field, a [release branch](#Release-Branches-and-Versioning) will be created and that version of the codebase will be considered 'stable'


## Code of Conduct
Contributors are expected to follow the Purdue Responsible Conduct of Research and related Purdue policies found here https://www.purdue.edu/policies/academic-research-affairs/s20.html. Be nice.
