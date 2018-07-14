import subprocess, shutil, os, re
from .cache_folder import CacheFolder
from ..flask_shared import app
from .validation_error import ValidationError

class MetadataParser:
    def __init__(self):
        self.fields_pattern = re.compile(r"___(\S+)___\s*=\s*(.+)\s*")
        self.docstring_pattern = re.compile(r'"""(.+?)"""', re.DOTALL)
        self.string_pattern = re.compile(r"'(.+)'|\"(.+)\"")
        self.list_pattern = re.compile(r"\[(.*?)\]")
        self.list_split_pattern = re.compile(r"\s*,\s*")

    def parse(self, filename, name, rules):
        with open(filename, "r") as file:
            return self.parse_str(file.read(), name, rules)

    # returns a dict in case of success and a list of errors otherwise
    def parse_str(self, input, name, rules):
        result = {}
        errors = []

        # docstring
        match = self.docstring_pattern.match(input)
        if match:
            result["docstring"] = match.group(1)

        # fields
        for key, value in self.fields_pattern.findall(input):
            result[key] = value

        for key, rule in rules.items():
            if key in result:
                if rule['type'] == 'string':
                    match = self.string_pattern.match(result[key])
                    if match:
                        result[key] = match.group(1) or match.group(2)
                    else:
                        errors.append(ValidationError(name, "%s metadata field has to be a string (surrounded by quotes)" % key))
                        continue
                if rule['type'] == 'list':
                    match = self.list_pattern.match(result[key])
                    if match:
                        result[key] = []
                        list_elements = [e for e in self.list_split_pattern.split(match.group(1)) if e]
                        for element in list_elements:
                            string_match = self.string_pattern.match(element)
                            if string_match:
                                result[key].append(string_match.group(1) or string_match.group(2))
                            else:
                                errors.append(ValidationError(name, "%s metadata list element %s has to be a string (surrounded by quotes)" % (key, element)))
                                continue
                    else:
                        errors.append(ValidationError(name, "%s metadata field has to be a list (surrounded by [])" % key))
                        continue
                if rule['type'] == 'boolean':
                    if result[key] not in ['True', 'False']:
                        errors.append(ValidationError(name, "%s metadata field has to be a boolean, please provide 'True' or 'False'" % key))
                        continue
                    result[key] = result[key] == 'True'
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
