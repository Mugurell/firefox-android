#!/usr/bin/env python3

"""
Scrapes GitHub labels for Fenix and generates a set of glean tags for use in metrics

See https://mozilla.github.io/glean/book/reference/yaml/tags.html
"""
import urllib
from pathlib import Path

import requests
import yaml

LICENSE_HEADER = """# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

GENERATED_HEADER = """
### This file was AUTOMATICALLY GENERATED by `./tools/update-glean-tags.py`
### DO NOT edit it by hand.

# Disable line-length rule because the links in the descriptions can be long
# yamllint disable rule:line-length
"""

TAGS_FILENAME = (Path(__file__).parent / "../app/tags.yaml").resolve()

labels = []
page = 1
while True:
    more_labels = requests.get(
        f"https://api.github.com/repos/mozilla-mobile/fenix/labels?per_page=100&page={page}"
    ).json()
    if not more_labels:
        break
    labels += more_labels
    page += 1

tags = {"$schema": "moz://mozilla.org/schemas/glean/tags/1-0-0"}
for label in labels:
    if label["name"].startswith("Feature:"):
        abbreviated_label = label["name"].replace("Feature:", "")
        url = (
            "https://github.com/mozilla-mobile/fenix/issues?q="
            + urllib.parse.quote_plus(f"label:{label['name']}")
        )
        label_description = (
            (label["description"].strip() + ". ") if len(label["description"]) else ""
        )
        tags[abbreviated_label] = {
            "description": f"{label_description}Corresponds to the [{label['name']}]({url}) label on GitHub."
        }

open(TAGS_FILENAME, "w").write(
    "{}\n{}\n\n".format(LICENSE_HEADER, GENERATED_HEADER)
    + yaml.dump(tags, width=78, explicit_start=True)
)
