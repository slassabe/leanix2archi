#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Main module
'''

import re
import pandas as pd
from customLog import get_default_logger

__author__ = "Serge LASSABE"
__copyright__ = "Copyright (C) 2023, Serge LASSABE"
__license__ = "agpl-3.0"
__version__ = "5.0.1"

Verbose = False

class Model():
    def __init__(self):
        self.logger = get_default_logger()
        self.warnings_collection = []
        self.elt_dict = {}      # {id1: Element1}
        self.rel_dict = {}      # {id1: Relationship1}
        self.tag_incr = 0
        self.tags_refs = {}     # {"tagName": "tagRef"}
        # Used in DrawioWriter(Writer) class
        self.refer_ids_to = {}  # {id_from1: [id_to1 id_to2]}
        self.refer_ids_from = {}# {id_to1: [id_from1 id_from2]}

    def get_checksum(self):
        return "E{}-R{}-P{}".format(len(self.get_elt_values()), len(self.get_rel_values()), len(self.get_rel_values()))
    def get_elt_keys(self):
        return list(self.elt_dict.keys())
    def get_elt_values(self):
        return list(self.elt_dict.values())
    def get_elt(self, id):
        if Verbose and not(self.elt_dict.get(id)):
            self.logger.error(f'>> get_elt: no element found for {id}')
        return self.elt_dict.get(id)
    def get_rel_keys(self):
        return list(self.rel_dict.keys())
    def get_rel_values(self):
        return list(self.rel_dict.values())
    def get_rel(self, id):
        if Verbose and not(self.elt_dict.get(id)):
            self.logger.error(f'>> get_rel: no element found for {id}')
        return self.rel_dict.get(id)

    def get_statistics(self):
        # Count elements
        elt_count_by_type = {}
        for elt in self.get_elt_values():
            previous_count = elt_count_by_type.get(elt.leanix_type)
            if previous_count:
                count = previous_count + 1
            else:
                count = 1
            elt_count_by_type[elt.leanix_type] = count
        # Count relationships
        rel_count_by_type = {}
        for rel in self.get_rel_values():
            previous_count = rel_count_by_type.get(rel.type)
            if previous_count:
                count = previous_count + 1
            else:
                count = 1
            rel_count_by_type[rel.type] = count

        return f'Statistics:\n- elements : {elt_count_by_type}\n- relations : {rel_count_by_type})'

    # Get and set refers as id
    def get_refer_ids_to(self, k):
        return self.refer_ids_to.setdefault(k, [])
    def get_refer_ids_from(self, k):
        return self.refer_ids_from.setdefault(k, [])

    # Convenient methods
    def dump(self):
        # Useed for debugging purpose
        result = f'{self}\n'
        result += f'elt_dict : {self.elt_dict}\n'
        result += f'rel_dict : {self.rel_dict}\n'
        result += f'tags_refs : {self.tags_refs}\n'
        return result

    WARNING_LABELS = {1: "Libellé d'interface contraire aux conventions de nommage (absence de source et destination)",
                      2: 'Absence de Producteur pour cette interface',
                      3: 'Absence de Producteur et Consommateur pour cette interface (suppression)',
                      4: 'Absence de Consommateur pour cette interface',
                      5: "Libellé d'interface contraire aux conventions de nommage (incohérence sur la source et/ou destination)"}
    def warning(self, type, ctxt, where):
        self.warnings_collection.append([f'WARNING({type})', self.WARNING_LABELS[type], ctxt])
        return

    def dump_warning(self, filename):
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df = pd.DataFrame(self.warnings_collection)
        df.columns = ['Type de Warning', 'Description du Warning', 'Contexte']
        df.to_excel(writer, index=False, header = True, sheet_name='Warning liste')
        writer.close()
        return

    def check_flow_name(self, name, id_provider, id_consumer):
        name_provider = self.get_elt(id_provider).leanix_name
        name_consumer = self.get_elt(id_consumer).leanix_name
        check = re.search(f"^.*\({name_provider.upper()} *- *{name_consumer.upper()}\)$",name.upper())
        if not check:
            self.warning(5, f'Interface : "{name}" - Producteur : "{name_provider}" - Consommateur : "{name_consumer}"', 'check_flow_name')
        return check


    def interface_name_beautifier(self, text):
        if not text:
            return ''
        else:
            result = text
            name_fields = text.split(' (', 2)
            if len(name_fields) > 1:
                result = name_fields[0]
            else:
                self.warning(1, f'"{text}"', 'interface_name_beautifier')
            return result

    # Used only for drawio, could be removed
    def set_refers_ids_to(self, k, v):
        return self.refer_ids_to.setdefault(k, []).append(v)
    def set_refers_ids_from(self, k, v):
        return self.refer_ids_from.setdefault(k, []).append(v)

    def get_projects(self):
        result = []
        for elt in self.get_elt_values():
            if elt.leanix_type == 'Project':
                self.logger.debug (f'FOUND : {elt.leanix_name}')
                result.append(elt.leanix_name)
        return result

class ModelItems():
    def __init__(self):
        self.logger = get_default_logger()
        self.tags = {}

    def set_tags(self, model, k, v):
        self.tags[k] = v
        if not model.tags_refs.get(k):
            model.tags_refs[k] = f'tag-property-ref{model.tag_incr}'
            model.tag_incr += 1

    def get_tags(self):
        return self.tags

class Element(ModelItems):
    def __init__(self, model, id, type, name, descr):
        super().__init__()
        self.leanix_id = id
        self.leanix_type = type
        self.leanix_name = name
        self.doc = descr
        model.elt_dict[id] = self

    def __str__(self):
        return f'Element(id = {self.leanix_id}, type = {self.leanix_type}, name = {self.leanix_name}, doc = ..., tags = {self.tags})'

class Relationship(ModelItems):
    def __init__(self, model, id, type, name, descr, src, target):
        super().__init__()
        self.leanix_id = id
        self.leanix_name = name # used only for Flow
        self.doc = descr        # used only for Flow
        self.type = type
        self.leanix_source = src
        self.leanix_target = target
        model.rel_dict[id] = self
        # Used only for drawio, could be removed
        if type == 'Flow':
            model.set_refers_ids_to(src, id)
            model.set_refers_ids_to(id, target)
            model.set_refers_ids_from(target, id)
            model.set_refers_ids_from(id, src)

    def __str__(self):
        return f'Relationship(id = {self.leanix_id}, type = {self.type}, name = {self.leanix_name}, src = {self.leanix_source}, target = {self.leanix_target}, doc = ..., tags = {self.tags})'


class Reader:
    def __init__ (self, model):
        self.logger = get_default_logger()
        self.model = model
        return

    def get_model(self):
        return self.model


class Writer():
    def __init__(self, model):
        self.logger = get_default_logger()
        self.model = model

    def __str__(self):
        return "Writer()"
