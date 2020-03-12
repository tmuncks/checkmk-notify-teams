#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Microsoft Teams
#
r"""
Send notification messages to Teams
===================================

Use a teams webhook to send notification messages
"""
import os
import requests
import sys

COLORS = {
    "CRITICAL": "#EE0000",
    "DOWN": "#EE0000",
    "WARNING": "#FFDD00",
    "OK": "#00CC00",
    "UP": "#00CC00",
    "UNKNOWN": "#CCCCCC",
    "UNREACHABLE": "#CCCCCC",
}


def teams_msg(context):
    """Build the message for teams"""
    facts = []

    # Service notification
    if context.get('WHAT', None) == "SERVICE":
        color = COLORS.get(context["SERVICESTATE"])
        title = "Service {NOTIFICATIONTYPE} notification".format(**context)
        facts.extend([
            {"name": "Service:", "value": context["SERVICEDESC"]},
            {"name": "Service state:", "value": context["SERVICESTATE"]},
            {"name": "Host:", "value": context["HOSTNAME"]}
        ])
        output = context["SERVICEOUTPUT"] if context["SERVICEOUTPUT"] else ""

    # Host notification
    else:
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
                # "activityTitle": "CheckMK",
                "activityTitle": title,
                # "activityImage": "https://checkmk.com/images/favicon.png",
                # "activitySubtitle": title,
                "facts": facts,
                "text": output
            }
        ]
    }


def collect_context():
    return {
        var[7:]: value.decode("utf-8")
        for (var, value) in os.environ.items()
        if var.startswith("NOTIFY_")
    }


def post_request(message_constructor, success_code=200):
    context = collect_context()

    url = context.get("PARAMETERS")
    r = requests.post(url=url, json=message_constructor(context))

    if r.status_code == success_code:
        sys.exit(0)
    else:
        sys.stderr.write(
            "Failed to send notification. Status: %i, Response: %s\n" % (r.status_code, r.text))
        sys.exit(2)


if __name__ == "__main__":
    post_request(teams_msg)
