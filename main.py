from atlassian import Jira
from requests import HTTPError

from bamboo import BambooBuildApi


class DeployTask(object):

    def __init__(self):
        self.envs = [];
        self.plan = None;
        self.build_number = 0;

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


field_deployment_env = 'Deploy environment'
field_build_task = 'Build Plan'
field_build_number = 'Build number'
deployment_branch = 'master'
jira = Jira('http://localhost:8080', token="NDA5MjgyNTI1NDQ5Op40xz7Gb86ceD4PlQqsimXo5V3r")
bamboo = BambooBuildApi(url='http://localhost:8085', token='MjMzOTg1MDk4MjM3OrANuM/c6f157lnAqQHaOEBjt6ju')

fields = jira.get_all_fields();
deploy_env = None
build_number = None
build_task = None

for field in fields:
    if field['name'] == field_deployment_env:
        deploy_env = field['id']
    elif field['name'] == field_build_task:
        build_plan_key = field['id']
    elif field['name'] == field_build_number:
        build_number = field['id']

issues = jira.jql('status="APPROVED" AND issuetype= deploy')
status = jira.get_all_statuses()

for issue in issues['issues']:

    task = DeployTask()
    envs = issue["fields"][deploy_env]
    for env in envs:
        if not env['disabled']:
            task.envs.append(env['value']);
    if len(task.envs) == 0:
        print("no env defined ,skip")
        continue
    task.build_number = int(issue["fields"][build_number]);
    task.plan = issue["fields"][build_plan_key]['value'];
    print(task)

    project = bamboo.get_deploy_project(task.plan);
    project_id = project['id']
    env_dic = dict(map(lambda x: (x['name'], x), project['environments']))

    for env in task.envs:
        if env not in env_dic.keys():
            print("env {0} not found".format(env))
            continue

    # get build branch , collect branch name as key
    branch = bamboo.get_branches(task.plan);
    branch_dic = dict(map(lambda x: (x['searchEntity']['branchName'], x['searchEntity']), branch['searchResults']))

    build_result_key = branch_dic[deployment_branch]['id'] + '-' + str(task.build_number)

    # make sure build is exists
    try:
        result = bamboo.build_result(build_result_key);

        # call api to get release version
        newReleaseName = bamboo.get_next_version(project_id, build_result_key)['nextVersionName']

        # build create new release base on
        new_version = bamboo.create_deployment(project_id, build_result_key, newReleaseName)

        for env in task.envs:
            # deploy to each environment
            bamboo.trigger_deployment(env_dic[env]['id'], new_version['id'])
        # assume resolution need to update in done
        jira.set_issue_status(issue['key'], 'Done', fields={"resolution": {'name': 'Done'}})

    except HTTPError as e:

        # play again if any error duration deployment
        jira.set_issue_status(issue['key'], 'PLANING')
        # log error in comment
        jira.issue_add_comment(issue['key'], e.response.text)
        pass
