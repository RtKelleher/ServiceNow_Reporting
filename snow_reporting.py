#!/usr/bin/env python3
# encoding: utf-8
""" Python script to create servicenow tickets from hive cases. Reducing the need for duplication in CMS.

"""
from cortexutils.responder import Responder
import requests
import yaml
import re
import json

with open("config.yml", "r") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)


class CreateCase(Responder):
    """ placeholder docstring

    """

    def __init__(self):
        Responder.__init__(self)
        self.url = self.get_param("config.url", None, "SN url is missing")
        self.user = self.get_param("config.user", None, "SN user is missing")
        self.pwd = self.get_param("config.password", None, "SN password missing")

    def operations(self, raw):
        return [
            (self.build_operation("AddTagToCase", tag="Responder:ServiceNow Case Created")),
            (self.build_operation("AddTagToCase", tag=str(self.response.json()["result"]["number"]))),
        ]

    def payload(self, cfg):
        payload = cfg["servicenow"]
        payload.add = cfg["hive"]
        payload.add = {
            "short_description": self.get_param("data.title", None),
            "comments": self.url + "/index.html#!/case/" + self.get_param("data._routing") + "/details",
            "assigned_to": self.get_param("data.owner") + "@" + cfg["servicenow"]["company"],
        }
        return payload

    def run(self):
        Responder.run(self)
        tags = self.get_param("data.tags", None)
        for tag in tags:
            check_for_SN = re.match(r"^[\w]{9}:[\w]{10}\W[\w]{4}\W[\w]{7}", tag)
            if not check_for_SN:
                headers = {"Content-Type": "application/json", "Accept": "application/json"}
                payload = payload(cfg)
                self.response = requests.post(
                    (self.url + "/api/now/table/incident"),
                    auth=(self.user, self.pwd),
                    headers=headers,
                    data=json.dumps(payload),
                )
                if self.response.status_code == 200 or self.response.status_code == 201:
                    self.report({"message": json.loads(self.response.text)})
                else:
                    self.error(self.response.status_code)
            else:
                self.error("Case already exists")


if __name__ == "__main__":
    CreateCase().run()
