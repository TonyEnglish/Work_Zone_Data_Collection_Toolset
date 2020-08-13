# Welcome

We're so glad you're thinking about contributing to a U.S. DOT Intelligent Transportations Systems Joint Program Office's (ITS JPO's) README template. If you're unsure about anything, just ask -- or submit the issue or pull request anyway. If you want to contact us outside GitHub, you can reach us at [data.itsjpo](mailto://data.itsjpo@dot.gov)

## Licensing Status

As noted in LICENSE, this project is in the worldwide public domain (in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the CC0 1.0 Universal public domain dedication).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.

# How to contribute to README Template

- Report bugs and request features via [Github Issues](https://github.com/usdot-jpo-codehub/codehub-readme-template/issues).
- [Email us](mailto://data.itsjpo@dot.gov.) your ideas on how to improve the README template. We're always open to suggestions.
- Create a [Github pull request](https://help.github.com/articles/creating-a-pull-request/) with new functionality or fixing a bug.
- Help us improve our best practices and formatting.
- Triage tickets and review update-tickets created by other users.

## Contributing Process

Most pull requests should go to the master branch and the change will be included in the next major/minor version release (e.g., 3.6.0 release). If you need to include a bug fix in a patch release (e.g., 3.5.2), make sure it’s already merged to master, and then create a pull request cherry-picking the commits from master branch to the release branch (e.g., branch 3.5.x).

For each pull request, an ITS CodeHub Support Team member will be assigned to review the pull request. For minor cleanups, the pull request may be merged right away after an initial review. For larger changes, we may have some comments or clarifications that will extend the time needed to complete. We will try to keep our response time within 7 days but if you don’t get any response in a few days, feel free to comment on the thread to get our attention. We also expect you to respond to our comments within a reasonable amount of time. If we don’t hear from you for 2 weeks or longer, we may close the pull request. You can still send the pull request again once you have time to work on it.

Once a pull request is merged, we will take care of the rest and get it into the final release.

## Issue Guidelines
In the interest of making it easier for our contributors to manage site issues, we request that issues follow certain guidelines.  Our developers mainly use [issues](https://github.com/usdot-jpo-codehub/codehub-readme-template/issues) to identify and prioritize their work. If you have questions about [ITS CodeHub](https://www.its.dot.gov/code/) or would like to start a general discussion, we kindly request that you email us at [data.itsjpo@dot.gov](mailto://data.itsjpo@dot.gov). We ask that you submit issues that are:
 - **Specific**: The issue makes specific requests. An example of a specific request would be `Reduce the Size of Images`. An example of a non-specific request would be `Improve Site Performance`.
 - **Measurable**: The issue has specific requirements and can be closed when those requirements are met. This helps us track the progress in addressing problems. For example, tech debt is always something to work on, so we should create separate issues for this, such as `Consolidate Styling of Repo and Task Cards` and `Convert Validator from Monaco Editor to jsoneditor`, rather than `Address Tech Debt`.
 - **Actionable**: An issue should request a specific action from a member of the ITS CodeHub team or community. An example of something actionable would be `Remove Invalid link`.  An example of something that isn't actionable by our team or community is `My city should be forking usdot-jpo-codehub.
 - **Realistic**: The issue is something that is achievable by the resources of the project, including contributions from the open source community. An example of a realistic issue is `Include Line Numbers in Template`.
 - **Time-Aware**: The issue is something that can be resolved within 6 months. If you think your issue might take longer, we encourage you to break up your issues into smaller issues (like stepping stones) that we can address. We can still work on big problems, but it is easier for us to track progress and identify what we need to work on, when big problems are broken up into smaller ones.
 
## Pull Request (PR) Guidelines

Create small PRs that are narrowly focused on addressing a single concern. We often receive PRs that are trying to fix several things at a time, but if only one fix is considered acceptable, no changes can be merged and both the author's and review's time is wasted. Create more PRs to address different concerns and everyone will be happy.

For speculative changes, consider opening an issue and discussing it with the ITS CodeHub team first. 

Provide a good PR description as a record of what change is being made and why it was made. Link to a GitHub issue if it exists. PRs with irrelevant changes won't be merged. 

Maintain clean commit history and use meaningful commit messages. PRs with messy commit history are difficult to review and may not be merged. Use rebase -i upstream/master to curate your commit history and/or to bring in latest changes from master (but avoid rebasing in the middle of a code review). Keep your PR up-to-date with upstream/master (if there are merge conflicts, we can't merge your change).

## Reviewer Guidelines

Apply the "release notes: yes" label if the pull request's description should be included in the next release (e.g., any new feature / bug fix). Apply the "release notes: no" label if the pull request's description should not be included in the next release (e.g., refactoring changes that does not change behavior, integration from Google internal, updating tests, etc.).

Contributions will be release in accordance with GitHub site policies (link to https://help.github.com/en/github/site-policy/github-terms-of-service#6-contributions-under-repository-license), including that contributions will be released under the same license applied to this repository.
