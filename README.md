 ## About the workflow

![product-screenshot]

This demo assumes project is running under above workflow.

Cronjob will poll the all  jira all `deploy` issues which under `APPROVED` status 

It will set the issue status to `DONE` if trigger deployment successfully and it will set status to `PLANING` and record reason as comment if failed .

## About the deploy issue type
![deploy-issue-type]

Sample assumed issue use customized field `Deployment environment`, `Build Plan`, `Build number` to link the deployment in bamboo.
and now I just assume we deploy from the build from the master branch.


[product-screenshot]: docs/workflow.png
[deploy-issue-type]: docs/issue-type.png

