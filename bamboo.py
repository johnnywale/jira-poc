from atlassian import Bamboo, Jira


class JiraApi(Jira):
    def trigger_deployment(self, environment_id, version_id):
        res = self.post('rest/api/latest/queue/deployment',
                        json='{}',
                        params={'environmentId': environment_id, "versionId": version_id})
        return res


class BambooBuildApi(Bamboo):
    """

    """

    def update_variable(self, plan_key, key, value):
        res = self.put('rest/api/latest/plan/' + plan_key + '/variables/' + key,
                       data={'name': key, "value": value})
        return res

    def create_variable(self, plan_key, key, value):
        res = self.post('rest/api/latest/plan/' + plan_key + '/variables',
                        json='{}',
                        params={'name': key, "value": value})
        return res

    def get_variable(self, plan_key, key):
        res = self.get('rest/api/latest/plan/' + plan_key + '/variables/' + key)
        return res

    def trigger_deployment(self, environment_id, version_id):
        res = self.post('rest/api/latest/queue/deployment',
                        json='{}',
                        params={'environmentId': environment_id, "versionId": version_id})
        return res

    def get_deploy_project(self, plan_key):
        response = self.get('rest/api/latest/deploy/project/all')
        for item in response:
            if item['planKey']['key'] == plan_key:
                return item

    def get_next_version(self, project_id, latest_result_key):
        response = self.get('rest/api/latest/deploy/preview/versionName', params={"deploymentProjectId": project_id,
                                                                                  "resultKey": latest_result_key})
        return response

    def get_latest_version(self, project_id, branch_key):
        response = self.get('rest/api/latest/deploy/project/' + str(project_id) + '/versions', params={
            "branchKey": branch_key})
        if response['size'] > 0:
            return response['versions'][0]
        return None

    def create_deployment(self, project_id, plan_result_key, release_name):
        res = self.post("rest/api/latest/deploy/project/" + str(project_id) + "/version",
                        data={"planResultKey": plan_result_key, "name": release_name})
        return res

    def get_branches(self, plan_key):
        response = self.get('rest/api/latest/search/branches', params={"searchTerm": "",
                                                                       "includeMasterBranch": 'true',
                                                                       "masterPlanKey": plan_key})
        return response
