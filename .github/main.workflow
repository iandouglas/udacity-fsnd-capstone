workflow "issues" {
  on       = "issues"
  resolves = ["Add an issue to project"]
}

action "Add an issue to project" {
  uses    = "docker://masutaka/github-actions-all-in-one-project:1.1.0"
  secrets = ["GITHUB_TOKEN"]
  args    = ["issue"]

  env = {
    PROJECT_URL         = "https://github.com/iandouglas/udacity-fsnd-capstone/projects/1"
    INITIAL_COLUMN_NAME = "To Do"
  }
}
