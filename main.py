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


field_deployment_env = 'Deploy Environment'
field_build_task = 'Build Plan'
field_software_version = 'Software Version'
deployment_branch = 'master'
jira = Jira('http://192.168.1.127:8080', token="NDIyODAxNzYzMDAwOvR9mI5jRgEhy9LPsv/FLjzvC/xV")
bamboo = BambooBuildApi(url='http://192.168.1.127:8085', token='MjMzOTg1MDk4MjM3OrANuM/c6f157lnAqQHaOEBjt6ju')

fields = jira.get_all_fields();
deploy_env = None
software_version = None
build_task = None

for field in fields:
    if field['name'] == field_deployment_env:
        deploy_env = field['id']
    elif field['name'] == field_build_task:
        build_plan_key = field['id']
    elif field['name'] == field_software_version:
        software_version = field['id']

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
    task.plan = issue["fields"][build_plan_key]['value'];

    sv = issue["fields"][software_version];
    var = bamboo.get_variable(task.plan, sv)['value'];
    task.build_number = int(var)
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
