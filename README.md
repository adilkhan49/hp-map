# hp-map

Regenerates a map using Github Actions to be embedded in a Wordpress site

## Set Up

1. Generate Service Account credentials for Google Sheets https://stateful.com/blog/google-sheets-api-tutorial
2. Save the JSON credentials in Github Action Secrets as key value pairs

## Schedule

Workflow is scheduled to run at 23:30 daily. To debug use on: workflow_dispatch

## Render

After code execution, `map.html` is refreshed and rendered online at https://github.com/adilkhan49/hp-map/blob/main/map.html

### Embed

The rendered map is embedded using an iframe in Wordpress

```
<iframe title="Humanity Project Map" src="https://raw.githack.com/adilkhan49/hp-map/main/map.html"  style="width:900px; height:900px; border: 1px solid black;"></iframe>
```
 
