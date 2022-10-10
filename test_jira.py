from jira import JIRA

jira_options = {'server': 'https://jira.bpcbt.com'}
jira = JIRA(options=jira_options, basic_auth=('Sklyankin', 'frIn9illa'))

jql = 'project = "SmartVista Presales Support" AND created > startOfYear() AND "Proposed Product improvements" is not EMPTY'
issues_list = jira.search_issues(jql)
for issue in issues_list :
    print('{}: {}'.format(issue.key, issue.fields.summary))
