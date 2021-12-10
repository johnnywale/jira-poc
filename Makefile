
vent:
	py -m venv venv

init:
	venv/scripts/pip install -r requirements.txt

jira:
	docker run -v d:/jira:/var/atlassian/application-data/jira --memory="6g" --name="jira" --env JVM_MINIMUM_MEMORY="4g" --env JVM_MAXIMUM_MEMORY="6g" -d -p 8080:8080 atlassian/jira-software

bamboo:
	docker run -v d:/bamboo:/var/atlassian/application-data/bamboo --name="bamboo" -d -p 8085:8085 -p 54663:54663 atlassian/bamboo

