# Wildfire Early Detection and Risk Assessment Platform — Team Ash Detectives

## Overview

This project is a **wildfire early-detection and risk-assessment platform** developed for **ECE444 – Software Engineering** at the University of Toronto.

The system combines environmental data, geospatial information, and AI/ML techniques to help detect potential wildfire events and communicate wildfire risk through an interactive map.

The platform aims to provide users with clear and accessible information about wildfire detections, environmental conditions, and risk levels while handling incomplete or unavailable data reliably.

## Key Features

- **Wildfire Detection** – Analyze available data to identify potential wildfire events.
- **Detection Results** – Display detected wildfire locations, timestamps, and confidence levels.
- **Wildfire Risk Assessment** – Calculate wildfire-risk levels using relevant environmental factors.
- **Interactive Risk Map** – Visualize wildfire-risk information geographically using a heatmap.
- **Risk Details** – Allow users to select an area and inspect detailed wildfire-risk information.
- **Environmental Data Handling** – Clearly identify missing or unavailable environmental information.
- **Failure Handling** – Gracefully handle failures involving external APIs, data sources, and model processing.
- **Modular Architecture** – Maintain clear interfaces between frontend, backend, AI/ML, and data-processing components.
- **Automated Testing** – Use automated tests and CI checks to protect critical functionality from regressions.

*These features represent the planned system capabilities and will be implemented incrementally.*

## System Architecture

The application is designed around four major components.

### Frontend

Provides the user interface and interactive wildfire map. It is responsible for displaying wildfire detections, risk information, environmental data, and system status.

### Backend

Provides APIs used by the frontend and coordinates communication between application components.

### AI/ML

Processes relevant input data to support wildfire detection and risk assessment.

### Data Processing

Collects, validates, and transforms environmental and geospatial data required by the application.

These components use clearly defined interfaces to reduce coupling and improve maintainability, extensibility, and testability.

## Requirements

The project's functional and non-functional requirements are documented in:

[docs/requirements.md](docs/requirements.md)

The requirements document contains the selected user stories, priorities, rationale, acceptance criteria, and references to the corresponding GitHub Issues.

## Project Management

Development is managed using **GitHub Issues** and a **GitHub Projects Kanban board**, following Agile software development practices.

User stories are prioritized based on their importance to the application's core functionality, dependencies, and implementation readiness.

Higher-priority user stories are selected for implementation during each sprint.

The project board follows the workflow:

**Todo → In Progress → Done**

### Project Management Tools

| Tool | Purpose | URL |
|---|---|---|
| GitHub Repository | Source code, documentation, and version control | [Repository](https://github.com/RianaMalhotra/ECE444-PROJECT) |
| GitHub Issues | User stories, requirements, bugs, and implementation tasks | [Issues](https://github.com/RianaMalhotra/ECE444-PROJECT/issues) |
| GitHub Projects | Kanban board for sprint planning, task prioritization, and progress tracking | [Project Board](https://github.com/users/RianaMalhotra/projects/1) |
| GitHub Pull Requests | Code review, collaboration, and integration of changes | [Pull Requests](https://github.com/RianaMalhotra/ECE444-PROJECT/pulls) |

### Sprint Planning and Tracking

The development process is organized into iterative sprints.

Each sprint includes:

1. **Backlog Prioritization** – Review and sort user stories according to their priority and dependencies.
2. **Sprint Planning** – Select high-priority stories and divide them into actionable development tasks.
3. **Task Estimation** – Estimate the hours required for each assigned task.
4. **Implementation** – Develop features using dedicated Git branches.
5. **Progress Tracking** – Update task status through GitHub Projects.
6. **Code Review** – Review changes through Pull Requests before merging.
7. **Sprint Review** – Compare estimated effort against actual time spent and identify improvements for the next sprint.

### Sprint Documentation

Sprint planning reports summarize completed work, planned tasks, estimated effort, and actual development time.

Reports are maintained in the repository as PDF documents.

Each report includes:

- A prioritized product backlog.
- A summary of the completed sprint.
- A plan for the following sprint.
- Individual task estimates and actual hours.
- Project management progress and supporting screenshots.

## Repository Structure

The current repository contains project documentation and team collaboration files. The application directories below represent the planned structure as implementation progresses.

```text
ECE444-PROJECT/
├── docs/
│   ├── requirements.md
│   └── sprint-report.pdf       
├── frontend/                # Planned UI and map components
├── backend/                 # Planned APIs and application logic
├── ml/                      # Planned detection and risk models
├── data-processing/         # Planned data ingestion and validation
├── tests/                   # Planned automated tests
├── README.md
├── CONTRIBUTION.md         
├── CODE_OF_CONDUCT.md       
├── team_members.md
└── team_workflow.md
```

The repository structure will evolve as additional application components are implemented.

## Testing

Automated testing is planned to protect critical functionality and identify regressions throughout development.

Testing will focus on:

- Core application functionality
- API behaviour and response validation
- Data validation and error handling
- AI/ML and risk-processing components
- Integration between major system components
- Regression prevention

Continuous integration checks will be introduced as the project develops to automate test execution and help maintain code quality.

## Development Workflow

Development follows an issue-driven workflow:

1. User stories and requirements are documented and linked to GitHub Issues.
2. High-priority user stories are selected during sprint planning.
3. Implementation work is divided into smaller development tasks with estimated effort.
4. Tasks are assigned and tracked using the GitHub Projects Kanban board.
5. Developers implement changes on dedicated Git branches.
6. Changes are submitted through Pull Requests for review.
7. Reviewed and approved changes are merged into the main branch.
8. Automated tests are introduced to verify functionality and reduce regressions.
9. Completed tasks and actual development hours are documented during sprint reviews.

## Contributing

Team members are expected to follow the project's collaborative development workflow.

Contributions should be associated with relevant GitHub Issues, implemented on dedicated branches, and reviewed through Pull Requests.

Detailed contribution guidelines are provided in [CONTRIBUTING.md](CONTRIBUTING.md).

All contributors are expected to follow the standards described in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Team

Developed by **Team Ash Detectives** as part of **ECE444 – Software Engineering** at the University of Toronto.

Team information and collaboration guidelines are available in:

- [Team Members](team_members.md)
- [Team Workflow](team_workflow.md)

## Project Status

🚧 **Under Development**

The project is currently progressing from requirements engineering into its first implementation sprint.

Development priorities include establishing the application structure, implementing high-priority user stories, and introducing foundational testing practices.

Progress is tracked through GitHub Issues, the GitHub Projects board, and sprint planning documentation.
