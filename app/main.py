#!/usr/bin/env python3
# encoding: utf-8

from re import template
from typing import Dict
from dataclasses import dataclass, field

from flask import Flask, jsonify
from werkzeug.routing import Rule
import hydra
from omegaconf import DictConfig, open_dict

import pycountry
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_number
from phonenumbers import geocoder
from phonenumbers import carrier

app = Flask(__name__)

@dataclass
class Phonenumber:
    phone: str
    format: Dict[str, str] =  field(default_factory=lambda: {"international":"", "local":""})
    valid: bool = False
    contry: Dict[str, str] = field(default_factory=lambda: {"code":"", "name": "", "prefix":""})
    location: str = ""
    carrier: str = ""

@app.route("/<number>", methods=["POST","GET"])
def phonenumber(number):
    """get the phonenumber information. Note only international coded numbering
    ---
    parameters:
        - name: number
          in: path
          type: string
          required: true
    responses:
        200: 
            description: A phone number structure
            schema:
                $ref: '#/definitions/Phonenumber'
        500:
            description: internal error
    definitions:
        Phonenumber:
            type: object
            properties:
                phone:
                    type: string
                format:
                    type: object
                    properties:
                        international:
                            type: string
                        local:
                            type: string
                valid:
                    type: bool
                contry:
                    type: object
                    properties:
                        code:
                            type: string
                        name:
                            type: string
                        prefix:
                            type: string
                location:
                    type: string
                carrier:
                    type: string
    """
    l = Phonenumber(phone=number)

    try:
        pn = phonenumbers.parse(number, None)
        l.phone=phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        l.format["international"] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
        l.format["local"] = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
        l.valid=phonenumbers.is_possible_number(pn)
        contry_code = region_code_for_number(pn)
        l.contry["code"]=contry_code
        l.contry["name"] = pycountry.countries.get(alpha_2=contry_code).name
        l.contry["prefix"]= "+" + str(phonenumbers.country_code_for_region(contry_code))
        l.carrier = carrier.name_for_number(pn, "en")
        l.location = geocoder.description_for_number(pn, "en")
    except:
        return "", 500

    return jsonify(l), 200

@app.endpoint("catch_all")
def _404(_404):
    return "", 404

app.url_map.add(Rule("/", defaults={"_404": ""}, endpoint="catch_all"))
app.url_map.add(Rule("/<path:_404>", endpoint="catch_all"))

@hydra.main(config_path="./",config_name="config.yaml", version_base=None)
def main(cfg: DictConfig):
    app.config.from_mapping(cfg.flask)
    with open_dict(cfg):
        del cfg["flask"]
    app.config["config"] = cfg
    app.run(host=cfg.server.host, port=cfg.server.port, debug=cfg.server.debug)

if __name__ == "__main__":
    main()