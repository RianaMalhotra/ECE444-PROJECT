# Contributing to Ash Detectives

Thanks for helping build our wildfire early-detection and risk-monitoring platform. This guide explains how we work together so that every change is easy to track, review and test. It applies to every team member and to anyone else who contributes.

## We develop with GitHub

We use GitHub to host code, track issues and user stories, and review changes through pull requests. We plan and track work on our **GitHub Projects** board, which is linked to this repository.

## How work is organized

- Every feature starts as a **user story issue** (for example, #10 Detection or #3 Heatmap).
- Each user story is split into **implementation issues**, and each implementation issue links back to its user story.
- Issues move across the board columns **Backlog → Ready → In Progress → In Review → Done**.
- The backlog is sorted by priority. Pick up work from **Ready**, starting at the top.
- Assign yourself to an issue before you start, so two people don't work on the same thing.

## Our workflow (GitHub Flow)

All code changes go through pull requests. Nobody pushes directly to `main`.

1. **Pull the latest `main`** before you start.
2. **Create a branch** for your issue, named after the issue number and a short description, such as `feature/21-risk-scoring-model` or `fix/27-unavailable-values`.
3. **Make small, focused commits** with clear messages that reference the issue, such as `Add confidence threshold config (#19)`.
4. **Add or update tests** for any code you add or change.
5. **Update documentation** (README, comments, interface docs) if you change how something works or is used.
6. **Make sure all tests pass** locally (and in CI once it is set up, #30).
7. **Open a pull request** into `main`:
   - Link the issue it closes (for example, `Closes #21`).
   - Describe what changed and how to test it.
   - Add screenshots for UI changes.
8. **Get at least one teammate's approval** before merging.
9. **Merge, delete your branch**, and move the issue to **Done** on the board.

## Reviewing pull requests

- Review your teammates' pull requests promptly, ideally within 24–48 hours.
- Check that the code works, follows our coding standards, includes tests, and meets the issue's acceptance criteria.
- Keep feedback specific, respectful and constructive. Explain the reason behind any requested change.
- If you're the author, respond to every comment, whether you make the change or explain why not.

## Reporting bugs

Report bugs by opening a new **GitHub issue**. A good bug report includes:

- A short summary of the problem
- Steps to reproduce it (as specific as possible)
- What you expected to happen
- What actually happened, with error messages or screenshots
- Any notes, such as what you've already tried or a guess at the cause

Label the issue `bug` and add it to the board so it can be prioritized.

## Suggesting features

Open an issue written as a user story ("As a [user], I want [goal] so that [benefit]"), with acceptance criteria. The team discusses it and decides where it goes in the backlog.

## Coding style

- Follow the repository structure and coding standards set by our Software Lead.
- Use clear, descriptive names for variables, functions and files.
- Keep functions small and focused on one job.
- Comment anything that isn't obvious, especially model logic, data cleaning steps and thresholds.
- Never commit secrets such as API keys or passwords. Use environment variables instead.
- Don't make up data. If an input is missing, mark the output as unavailable or incomplete (see #27 and #28).

## Communication

- Use issue and pull request comments for anything tied to specific work, so decisions are recorded.
- Raise blockers early in team meetings or our group chat.
- If you can't finish an assigned task in the sprint, tell the team so it can be carried over or reassigned.

## Code of Conduct

By contributing, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Report concerns to riana.malhotra@mail.utoronto.ca (main contact) or ireen.cheralody@mail.utoronto.ca (alternative contact).

## References

This document was adapted from the open-source contribution guidelines template by Brian A. Danielak (https://gist.github.com/briandk/3d2e8b3ec8daf5a27a62), which is itself based on Facebook's Draft.js contributing guide.
