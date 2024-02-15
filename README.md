## Installation notes

#### Virtual environment
Please, use a virtual environment
`python -m venv .venv` to create it
To activate it, either
`./.venv/Scripts/activate` or `source ./.venv/Scripts/activate`

#### Dependency install
From root folder do
`python -m pip install -e .`
Will install the project as `src` so that relative paths can be used
Watch out if you have any other `src` dependencies you might have used for other projects.