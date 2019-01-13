#!/usr/bin/env python3
import datetime
import boto3
import slackweb
import time
import os
from urllib.parse import parse_qs

DEFAULT_COST_TYPE = 'aws'
cd = boto3.client('ce', 'us-east-1')
SLACK_USER_NAME = os.environ["slack_user_name"]
SLACK_WEB_HOOK = os.environ["slack_web_hook"]
TOKEN = os.environ["token"]
DEFAULT_CHANNEL = os.environ["slack_default_channel"]
TAG_NAME = os.environ["tag_name"]

slack = slackweb.Slack(url=SLACK_WEB_HOOK)


def get_command_details(arguments):
    argument_list = arguments.split()
    argument_count = len(argument_list)
    cost_type = DEFAULT_COST_TYPE
    today = datetime.datetime.today()
    first_of_this_month = datetime.date(day=1, month=today.month, year=today.year)
    prev_month_end = first_of_this_month - datetime.timedelta(days=1)
    prev_month_start = datetime.date(day=1, month=prev_month_end.month, year=prev_month_end.year)
    start_date = prev_month_start
    end_date = first_of_this_month
    if argument_count > 0:
        if argument_list[0] in ['aws']:
            cost_type = argument_list[0]
        if argument_count >= 3:
            startdate = argument_list[1]
            start_date = datetime.datetime.strptime(startdate, '%Y-%m-%d')
            enddate = argument_list[2]
            end_date = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    return (cost_type, start_date, end_date)


def get_cost_details(command_details, type, key):
    results = []
    # dataReq = []
    token = None
    while True:
        if token:
            kwargs = {'NextPageToken': token}
        else:
            kwargs = {}
        data = cd.get_cost_and_usage(TimePeriod={'Start': command_details[1].strftime('%Y-%m-%d'),
                                                 'End': command_details[2].strftime('%Y-%m-%d')},
                                     Granularity='MONTHLY',
                                     Metrics=['UnblendedCost'],
                                     GroupBy=[{'Type': 'DIMENSION',
                                               'Key': 'LINKED_ACCOUNT'},
                                              {'Type': type, 'Key': key}], **kwargs)
        results += data['ResultsByTime']
        token = data.get('NextPageToken')
        if not token:
            break

    return results


def get_slack_attachment(bu_cost_dict, command_details):
    fields_list = []
    fields_list.append({"title": "Tag Name", "value": "", "short": True})
    fields_list.append({"title": "Cost Usage (in USD)", "value": "", "short": True})
    for bu_name, cost in bu_cost_dict.items():
        fields_list.append({"title": "", "value": bu_name, "short": True})
        fields_list.append({"title": "", "value": cost, "short": True})
    attachment = {
        "text": "Aws cost usage report:- From: " + command_details[1].strftime('%Y-%m-%d')
                + " To " + command_details[2].strftime('%Y-%m-%d') + " (Exclude)",
        "fields": fields_list,
        "footer": "SecTechOPS Team",
        "ts": time.time(),
        "color": "#3C0639"
    }

    return attachment


def get_buwise_cost(results, remove_string, include_blank=True):
    bu_dict = dict()
    for result_by_time in results:
        for group in result_by_time['Groups']:
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            amount = float("%0.2f" % (amount))
            # unit = group['Metrics']['UnblendedCost']['Unit']
            tag_name = group['Keys'][1].replace(remove_string, '')
            bu_name = tag_name.lower()
            if tag_name == '' and include_blank:
                bu_name = 'notag'
            if bu_dict.get(bu_name):
                existing_cost = bu_dict[bu_name]
                bu_dict[bu_name] = existing_cost + amount
            else:
                bu_dict[bu_name] = amount
    return bu_dict


def main(event=None, context=None):
    details = dict()
    if event.get('body'):
        body = event['body']
        details = parse_qs(body)
    channel_name = DEFAULT_CHANNEL
    if details.get('channel_id'):
        channel_name = details['channel_id'][0]
    arguments = ''
    if details.get('text'):
        arguments = details['text'][0]

    command_details = get_command_details(arguments)
    attachments = []
    if command_details[0] == 'aws':
        results = get_cost_details(command_details, 'TAG', TAG_NAME)
        bu_cost_dict = get_buwise_cost(results, TAG_NAME + '$')
        slack_attachment = get_slack_attachment(bu_cost_dict, command_details)
        attachments.append(slack_attachment)
        slack.notify(attachments=attachments, channel=channel_name, username=SLACK_USER_NAME, icon_emoji=':bar_chart:')
        response = {"statusCode": 200}
        return response
    else:
        response = {"statusCode": 400}
        return response


if __name__ == '__main__':
    main()
