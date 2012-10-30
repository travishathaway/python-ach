from data_types import (Header, FileControl, BatchHeader, BatchControl,
                        EntryDetail, AddendaRecord) 
from settings import *

from datetime import datetime

class AchFile(object):

    """
    Holds:

    Header (1)
    Batch  (n) <-- multiple
    Footer (1)

    What else this needs to do:
        - Calculate Control fields and credate a FileControl object
            - get_batch_count
            - get_block_count
            - get_entry_add_count
            - get_entry_hash
            - get_total_debit
            - get_total_credit
    """

    def __init__(self, file_id_mod):
        """
        args: header (Header), batches (List[FileBatch]), control (FileControl)t
        """

        self.header  = Header(IMMEDIATE_DEST,IMMEDIATE_ORG,file_id_mod,IMMEDIATE_DEST_NAME,
                                IMMEDIATE_ORG_NAME,)
        self.batches = list()

    def add_batch(self,std_ent_cls_code,batch_info=list(),credits=False,debits=False):

        entry_desc = self.get_entry_desc(std_ent_cls_code)

        batch_count = len(self.batches) + 1

        datestamp = datetime.today().strftime('%y%m%d') #YYMMDD

        if credits and debits:
            serv_cls_code = '200'
        elif credits:
            serv_cls_code = '220'
        elif debits:
            serv_cls_code = '225'

        batch_header = BatchHeader(serv_cls_code=serv_cls_code,company_name=IMMEDIATE_ORG_NAME,
                                    company_id=COMPANY_ID, std_ent_cls_code=std_ent_cls_code,
                                    entry_desc=entry_desc, desc_date='', eff_ent_date=datestamp,
                                    orig_stat_code='1', orig_dfi_id=ORIG_DFI_ID,batch_id=batch_count)

        entries = list()
        entry_counter = 1

        for record in batch_info:
            entry = EntryDetail(std_ent_cls_code)

            entry.transaction_code = record['type']
            entry.recv_dfi_id = record['routing_number']
            
            if len(record['routing_number']) < 9:
                entry.calc_check_digit()
            else:
                entry.check_digit = record['routing_number'][8]

            entry.dfi_acnt_num  = record['account_number']
            entry.amount        = int(record['amount']) * 100
            entry.ind_name      = record['name'].upper()[:22]
            entry.trace_num     = ORIG_DFI_ID + entry.validate_numeric_field(entry_counter, 7)

            entries.append(entry)
            entry_counter += 1

        self.batches.append( FileBatch( batch_header, entries ) )

        
    def get_entry_desc(self, std_ent_cls_code):

        if std_ent_cls_code == 'PPD':
            entry_desc = 'PAYROLL'
        elif std_ent_cls_code == 'CCD':
            entry_desc = 'DUES'
        else:
            entry_desc = 'OTHER'

        return entry_desc

    def render_to_string(self):
        """
        Renders a nacha file as a string
        """

        ret_string = self.header.get_row() + "\n"

        for batch in self.batches:
            ret_string += batch.render_to_string()

        #ret_string += self.control.get_row()

        return ret_string

class FileBatch(object):

    """
    Holds:

    BatchHeader  (1)
    Entry        (n) <-- multiple
    BatchControl (1)
    """

    def __init__(self, batch_header, entries):
        """
        args: batch_header (BatchHeader), entries (List[FileEntry])
        """

        self.batch_header   = batch_header
        self.entries        = entries

        #set up batch_control 

        batch_control = BatchControl(self.batch_header.serv_cls_code)


        self.batch_control = batch_control
    def render_to_string(self):
        """
        Renders a nacha file batch to string
        """

        ret_string = self.batch_header.get_row() + "\n"

        for entry in self.entries:
            ret_string += entry.get_row() + "\n"

        ret_string += self.batch_control.get_row() + "\n"

        return ret_string

class FileEntry(object):

    """
    Holds:

    EntryDetail (1)
    AddendaRecord (n) <-- for some types of entries there can be more than one
    """

    def __init__(self, entry_detail, addenda_record):
        """
        args: entry_detail( EntryDetail), addenda_record (List[AddendaRecord])
        """

        self.entry_detail   = entry_detail
        self.addenda_record = addenda_record

    def render_to_string(self):
        """
        Renders a nacha batch entry and addenda to string
        """
        
        ret_string = self.entry_detail.get_row() + "\n"
        
        for addenda in self.addenda_record:
            ret_string += addenda.get_row() + "\n"

        return ret_string
