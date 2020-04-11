#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Microsoft Teams
#
"""
Send notification messages to Teams
===================================

Use a teams webhook to send notification messages
"""
import os
import requests
import sys


# Define icons as links or image data
ICONS = {
    '_GOOD': "https://tmuncks.github.io/checkmk-notify-teams/images/good.png",
    '_WARN': "https://tmuncks.github.io/checkmk-notify-teams/images/warning.png",
    '_CRIT': "https://tmuncks.github.io/checkmk-notify-teams/images/critical.png",
    '_UNKN': "https://tmuncks.github.io/checkmk-notify-teams/images/unknown.png",
    '_UNRE': "https://tmuncks.github.io/checkmk-notify-teams/images/unreachable.png",
}

# Reference icons for all possible states
ICONS.update({
    # Host states
    'UP': ICONS.get('_GOOD'),
    'DOWN': ICONS.get('_CRIT'),
    'UNREACHABLE': ICONS.get('_UNRE'),
    # Service states
    'OK': ICONS.get('_GOOD'),
    'WARNING': ICONS.get('_WARN'),
    'CRITICAL': ICONS.get('_CRIT'),
    'UNKNOWN': ICONS.get('_UNKN'),
})

# Define colors for all possible states
COLORS = {
    # Host states
    'UP': "#69c92e",
    'DOWN': "#df0000",
    'UNREACHABLE': "#e16d00",
    # Service states
    'OK': "#69c92e",
    'WARNING': "#ffb200",
    'CRITICAL': "#df0000",
    'UNKNOWN': "#e16d00",
}


def teams_msg(context):
    """Build the message for teams"""
    facts = []

    # Service notification
    if context.get('WHAT', None) == "SERVICE":
        icon = ICONS.get(context["SERVICESTATE"])
        color = COLORS.get(context["SERVICESTATE"])
        title = "Service {NOTIFICATIONTYPE} notification".format(**context)
        facts.extend([
            {"name": "Host:", "value": context["HOSTNAME"]},
            {"name": "Service:", "value": context["SERVICEDESC"]},
            {"name": "Service state:", "value": context["SERVICESTATE"]}
        ])
        output = context["SERVICEOUTPUT"] if context["SERVICEOUTPUT"] else ""

    # Host notification
    else:
        icon = ICONS.get(context["HOSTSTATE"])
        color = COLORS.get(context["HOSTSTATE"])
        title = "Host {NOTIFICATIONTYPE} notification".format(**context)
        facts.extend([
            {"name": "Host:", "value": context["HOSTNAME"]},
            {"name": "Host state:", "value": context["HOSTSTATE"]}
        ])
        output = context["HOSTOUTPUT"] if context["HOSTOUTPUT"] else ""

    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": title,
        "themeColor": color,
        "sections": [
            {
                "activityTitle": title,
                "activityText": output,
                "activityImage": icon,
                "facts": facts
            }
        ]
    }


def collect_context():
    return {var[7:]: value.decode("utf-8") for (var, value) in os.environ.items() if var.startswith("NOTIFY_")}


def post_request(message_constructor, success_code=200):
    context = collect_context()

    url = context.get("PARAMETERS")
    r = requests.post(url=url, json=message_constructor(context))

    if r.status_code == success_code:
        sys.exit(0)
    else:
        sys.stderr.write("Failed to send notification. Status: %i, Response: %s\n" % (r.status_code, r.text))
        sys.exit(2)


if __name__ == "__main__":
    post_request(teams_msg)
