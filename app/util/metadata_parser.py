import subprocess, shutil, os, re
from .cache_folder import CacheFolder
from ..flask_shared import app
from .validation_error import ValidationError

class MetadataParser:
    def __init__(self):
        self.line_pattern = re.compile(r"###\s*(\S*)\s*:\s*(.*)")
        self.split_pattern = re.compile(r"\s*,\s*")

    def parse(self, filename, name, rules):
        with open(filename, "r") as file:
            return self.parse_str(file.read(), name, rules)

    # returns a dict in case of success and a list of errors otherwise
    def parse_str(self, input, name, rules):
        lines = input.splitlines()
        result = {}
        errors = []
        for line in lines:
            matches = self.line_pattern.match(line)
            if matches == None:
                break
            key = matches.group(1).lower()
            value = matches.group(2)

            if key not in rules:
                errors.append(ValidationError(name, "%s is not an allowed metadata field: %s" % (key, sorted(list(rules.keys())))))
                continue

            result[key] = value

        for key, rule in rules.items():
            if key in result:
                if rule['type'] == 'list':
                    result[key] = [e for e in self.split_pattern.split(result[key]) if e]
                if rule['type'] == 'boolean':
                    if result[key].lower() not in ['yes', 'no']:
                        errors.append(ValidationError(name, "%s metadata field has to be a boolean, please provide 'yes' or 'no'" % key))
                        continue
                    result[key] = result[key].lower() == 'yes'
                if ('min' in rule) and len(result[key]) < rule['min']:
                    errors.append(ValidationError(name, "%s metadata field has a minimum length of %d, provided: %d" % (key, rule['min'], len(result[key]))))
                    continue
                if ('max' in rule) and len(result[key]) > rule['max']:
                    errors.append(ValidationError(name, "%s metadata field has a maximum length of %d, provided: %d" % (key, rule['max'], len(result[key]))))
                    continue
            else:
                if 'required' in rule and rule['required']:
                    errors.append(ValidationError(name, "%s metadata field is required but not found" % key))
                    continue
                if 'default' in rule:
                    result[key] = rule['default']

        return errors or result
