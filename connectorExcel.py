#!/usr/bin/env python
# coding: utf-8

'''
 Purpose :
   Dump LeanIx and convert output in various file format
   - Export Excel Files
'''

import pandas as pd
import xlsxwriter
from leanIXConverterModels import Model, Writer
from customLog import get_default_logger

__author__ = "Serge LASSABE"
__copyright__ = "Copyright (C) 2023, Serge LASSABE"
__license__ = "agpl-3.0"
__version__ = "5.0.1"

ELT_COLUMNS = ['id',  'type', 'name', 'description']
REL_COLUMNS_SHORT = ['id',  'type', 'name', 'description',  'relToProvider', 'relToConsumer']
REL_COLUMNS_LONG = ['id',  'type', 'name', 'description',  'relToProvider', 'ProviderName', 'relToConsumer', 'ConsumerName']
ELT_SHEET_NAME = 'Element'
REL_SHEET_NAME = 'Relationship'

class ExcelWriter(Writer):
    def dump(self, filename):
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df = pd.DataFrame(ExcelElement(self.model).to_data_collection())
        df.columns = ELT_COLUMNS
        if False:   # Filter Application only
            is_application = df['type'] == 'Application'
            extract_df = df[is_application]
        else:
            extract_df = df
        extract_df.to_excel(writer, index=False, header = True, sheet_name=ELT_SHEET_NAME)

        df = pd.DataFrame(ExcelRelationship(self.model).to_data_collection())
        df.columns = REL_COLUMNS_LONG
        if False:   # Filter Application only
            is_flow = df['type'] == 'Flow'
            extract_df = df[is_flow]
        else:
            extract_df = df
        extract_df.to_excel(writer, index=False, header = True, sheet_name=REL_SHEET_NAME)
        writer.close()

class ExcelElement(ExcelWriter):
    def to_data_collection(self):
        data_collection = []
        for elt in self.model.get_elt_values():
            row = [elt.leanix_id, elt.leanix_type, elt.leanix_name, elt.doc]
            data_collection.append(row)
        return data_collection

class ExcelRelationship(ExcelWriter):
    def to_data_collection(self):
        data_collection = []
        for rel in self.model.get_rel_values():
            src_id = rel.leanix_source
            src_name = self.model.get_elt(src_id).leanix_name
            target_id = rel.leanix_target
            target_name = self.model.get_elt(target_id).leanix_name
            row = [rel.leanix_id, rel.type, rel.leanix_name, rel.doc, src_id, src_name, target_id, target_name]
            data_collection.append(row)
        return data_collection
