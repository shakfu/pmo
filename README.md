# pmo
An sqlalchemy schema for a project mgmt system.

Generates a graphviz graph.


## Requirements

Requires `sqlalchemy`, `graphviz`

Development requirements: `pytest`

## Concepts

- OKR consists of an `Objective`, which tells you where to go.
Several `KeyResult`s , which are the measurable results you need to achieve
to get to your `Objective`. And `Initiative`s, which are all the projects and
tasks that will help you achieve your `KeyResult`s.
