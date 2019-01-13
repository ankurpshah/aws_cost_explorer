# aws_cost_explorer
Slack command provides Business unit wise AWS costs based on tags

## What is aws cost usage report.
* This is to get the cost usage of aws resources (from all accounts) per business unit wise, for the given date range. (Default date will be the previous month, if no custom date provided in the input on slash command.)

* This is integrated with slack slash command, ie we can issue the command from slack from any channel and get the report immediately on the same slack channel.


## Prerequisite
* Account on aws.
* [serverless](https://serverless.com/framework/?gclid=EAIaIQobChMIoq-B4c_O3wIVDIJpCh123Q7JEAAYASAAEgJqe_D_BwE) framework installed on the system.
* Account on serverless.


## Serverless Framework Installation.
* [Install the serverless framework cli](https://serverless.com/framework/docs/providers/aws/guide/installation/) with the below command.

  `npm install -g serverless`

* Verify that Serverless is installed with the below command.

  `serverless --version` or `sls --version`

* Log into serverless portal with the below command which will open the portal in the browser.

  `sls login`

## Deployment into aws lambda using Serverless Framework.
* We are using the below two serverless plugins which needs to be installed on the system before the deployment.
  1. serverless-prune-plugin
  2. serverless-python-requirements

* Command to install these plugins.
  1. `sls plugin install -n serverless-prune-plugin`
  2. `sls plugin install -n serverless-python-requirements`

* Run the below command from the directory where the 'serverless.yaml' present which will have the details of the function.

  `sls deploy`

## Configuration
* Configure `slack_web_hook`, `slack_user_name`, slack `token` and `slack_default_channel`
* Configure `tag_name` that marks different business units.

## Verification/Test of serverless deployment
* We can verify the deployment using follwing command.

  `sls deploy list functions`

* Output should show *aws-cost-usage* in list with the Version details.

* Run the below command for more details of the deployed function.

  `sls info`

* Output will have details of the service name, function name, endpoint  and the stage of the deployment.

* Run the below command to invoke the function.

  `sls invoke -f aws-cost-usage`

* Update on serverless.yaml and before deployment, run the below local invoke command to test.

  `sls local invoke -f aws-cost-usage`

* function logs

  `sls logs -f <function name>`

  `sls logs -f aws-cost-usage`

## Verification/Test of slack slash command.

* Run the below command from slack fron any channel to get the report.

  `/cost` - AWS Cost will be generated on the same channel for the previous month.

  `/cost aws` - AWS Cost will be generated on the same channel for the previous month.

  `/cost aws start_date end_date`  (date format: yyyy-mm-dd): Report generated for the given custom dates.

## View on Serverless dashboard.

* [Login to serverless portal](https://dashboard.serverless.com/tenants/prognos/applications/)
* We can view the deployed functions inside the prognos tenant and deployed details can be be viewed for the deployed functions.

## Enviornment Variables
* We can invoke the function using local variables as below.

  `serverless invoke local -f aws-cost-usage -e slack_default_channel="#devnull"`

## Support
* For any issues or changes please contact @ankurpshah