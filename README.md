# hp-map

How to use Github Actions to refresh content on Wordpress


Requirements:
- Process should retrieve data from a Google Sheet
- Credentials must be stored securely
- Schedule as a CRON job

## Set Up


1. Clone this repository
6. Generate Google Service Account credentials https://stateful.com/blog/google-sheets-api-tutorial
2. Modify Python code as needed
7. Store credentials in a .env file
8. Change the workflow YAML to run `on: workflow_dispatch`
9. Commit code to a Github Repo
10. Upload the .env to Github Secrets as key-value pairs
11. Navigate to Githubn/Actions to test the Workflow
12. After debugging, edit the YAML to be triggered `on: schedule`


## Schedule

Workflow is scheduled to run at 23:30 daily.

With `on: workflow_dispatch` you can run the manually and take user input, but only in the default branch.

## Execute

A YAML file in `.githhub/workflows/` clones the repository, adds secrets to a .env file, installs Python & dependencies, runs a Python programme and finally commits changes to the main branch. 

Updates to `map.html` are rendered on [githack](https://raw.githack.com/adilkhan49/hp-map/main/map.html) are picked up within minutes.

## Embed

The githack page is embedded using an iframe in Wordpress. 

```
<iframe
   title="Humanity Project Map"
   src="https://raw.githack.com/adilkhan49/hp-map/main/map.html"
   style="
      width:900px;
      height:900px;
      border: 1px solid black;"
></iframe>
```
 
### Cost (As of May 2024)

- If the repository is private then the Githun Action costs nothing. Otherwise see [here](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions#per-minute-rates) for per minute rates
- A Wordpress site costs between £3 and £51 per month


