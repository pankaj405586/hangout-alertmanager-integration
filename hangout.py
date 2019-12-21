#!/usr/bin/env python
import json

from flask import Flask, jsonify, request, Response
from httplib2 import Http

app = Flask(__name__)

rooms = {
            "prometheus-alerts": "your_webhookurl",
        }


@app.route('/alert', methods=['POST'])
def devops_hangout():
    raw_post_data = request.data
    post_data = json.loads(raw_post_data)
    alerts = post_data.get("alerts", [])
    if not alerts:
        return Response("No alerts found", status=400)

    for alert in alerts:
        print("Doing for %s" % alert)
        status = alert.get("status")
        print("Status: %s" %status)
        labels = alert.get("labels")
        if not labels:
            print("No labels found")
            continue

        annotations = alert.get("annotations")
        if not annotations:
            print("no annotations found ")
            continue

        name        = labels.get('name', "UnKnown")
        severity    = labels.get('severity', None)
        alert_name  = labels.get('alertname', None)
        machine_ip  = labels.get('private_ip')
        source      = labels.get('job')
        team        = labels.get('team')
        description = annotations.get('description')

        message_body = prepare_card(status,alert_name, machine_ip, name, source, severity, team, description)
        print("Calling card now...")
        success = make_request_to_chat(message_body, rooms.get("prometheus-alerts"))

        if not success:
            print("Error in calling CHAT API")

    return Response("success", status=200)



def prepare_card(status,alert_name, machine_ip, name, source, severity, team, description):
    """
    Prepare card for sending
    :param status:
    :param alert_name:
    :param machine_ip:
    :param name:
    :param source:
    :param severity:
    :param team:
    :param description:
    :return:
    """

    if not status or not alert_name or not machine_ip or not name or not source or not severity or not team or not description:
        print("ERROR... DATA MISSING for %s %s %s %s %s %s" % (status,alert_name, machine_ip, name, source, severity, team, description))
        return

    status_color = "#ef3211"
    if "RESOLVED" == status.upper():
        status_color = "#228C22"
        severity = "OK"

    return {
        "cards": [
            {
              "header": {
                "title": "<b>" + alert_name + "</b>",
                "imageUrl": "https://i2.wp.com/kubedex.com/wp-content/uploads/2018/09/prometheus-1.png?w=400&ssl=1"
              },
              "sections": [
                {
                  "widgets": [
                      {
                        "keyValue": {
                          "topLabel": "Severity",
                          "content": "<b><font color=' " + status_color + "'>" + severity.upper() + "</font></b>"
                          }
                      },

                      {
                        "keyValue": {
                          "topLabel": "Machine IP",
                          "content": "<b>" + machine_ip + "</b>"
                          }
                      },
                      {
                          "keyValue": {
                              "topLabel": "HostName",
                              "content": "<b>" + name + "</b>"
                          }
                      },
                      {
                        "keyValue": {
                          "topLabel": "POD",
                          "content": "<b>" + team.upper() + "</b>"
                          }
                      },
                      {
                          "keyValue": {
                              "topLabel": "Source",
                              "content": "<b>" + source.upper() + "</b>"
                          }
                      }
                  ]
                },
                {
                  "header": "Description",
                  "widgets": [
                    {
                      "textParagraph": {
                        "text": description
                      }
                    },
                  ]
                }
              ]
            }
          ]
    }


def make_request_to_chat(body, room_name):
    """
    Message body
    :param body:
    :return:
    """
    if not body:
        return
    http_obj = Http()
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    response = http_obj.request(
        uri=room_name,
        method='POST',
        headers=headers,
        body=json.dumps(body),
    )
    if not response:
        return False
    else:
        code = response[0].status
        return code == 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
