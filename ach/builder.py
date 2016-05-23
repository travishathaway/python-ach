import math
from datetime import datetime, timedelta

from .data_types import (
    Header, FileControl, BatchHeader,
    BatchControl, EntryDetail, AddendaRecord
)


class AchFile(object):
    """
    This class is what stores the ach data.  Its main external methods
    are `add_batch` and `render_to_string`.

    """

    def __init__(self, file_id_mod, settings):
        """
        The file_id_mod should be 'A' for the first of the day, 'B'
        for the second and so on.
        """

        self.settings = settings

        try:
            self.header = Header(
                settings['immediate_dest'],
                settings['immediate_org'], file_id_mod,
                settings['immediate_dest_name'], settings['immediate_org_name']
            )
        except KeyError:
            raise Exception(
                'Settings require: "immediate_dest", "immediate_org", \
                immediate_dest_name", and "immediate_org_name"'
            )

        self.batches = list()

    def add_batch(self, std_ent_cls_code, batch_entries=None,
                  credits=True, debits=False, eff_ent_date=None,
                  company_id=None):
        """
        Use this to add batches to the file. For valid std_ent_cls_codes see:
        http://en.wikipedia.org/wiki/Automated_Clearing_House#SEC_codes
        """
        if batch_entries is None:
            batch_entries = list()

        entry_desc = self.get_entry_desc(std_ent_cls_code)

        batch_count = len(self.batches) + 1

        if not eff_ent_date:
            eff_ent_date = datetime.today() + timedelta(days=1)

        if credits and debits:
            serv_cls_code = '200'
        elif credits:
            serv_cls_code = '220'
        elif debits:
            serv_cls_code = '225'

        batch_header = BatchHeader(
            serv_cls_code=serv_cls_code,
            batch_id=batch_count,
            company_id=company_id or self.settings['company_id'],
            std_ent_cls_code=std_ent_cls_code,
            entry_desc=entry_desc,
            desc_date='',
            eff_ent_date=eff_ent_date.strftime('%y%m%d'),  # YYMMDD
            orig_stat_code='1',
            orig_dfi_id=self.settings['immediate_dest'][:8],
            company_name=self.settings['immediate_org_name']
        )

        entries = []
        entry_counter = 1

        for record in batch_entries:

            entry = EntryDetail(
                std_ent_cls_code=std_ent_cls_code,
                id_number=record.get('id_number', ''),
            )

            entry.transaction_code = record.get('type')
            entry.recv_dfi_id = record.get('routing_number')

            if len(record['routing_number']) < 9:
                entry.calc_check_digit()
            else:
                entry.check_digit = record['routing_number'][8]

            entry.dfi_acnt_num = record['account_number']
            entry.amount = int(round(float(record['amount']) * 100))
            entry.ind_name = record['name'].upper()[:22]
            entry.trace_num = self.settings['immediate_dest'][:8] \
                + entry.validate_numeric_field(entry_counter, 7)

            entries.append((entry, record.get('addenda', [])))
            entry_counter += 1

        self.batches.append(FileBatch(batch_header, entries))
        self.set_control()

    def set_control(self):

        batch_count = len(self.batches)
        block_count = self.get_block_count(self.batches)
        entry_hash = self.get_entry_hash(self.batches)
        entadd_count = self.get_entadd_count(self.batches)
        debit_amount = self.get_debit_amount(self.batches)
        credit_amount = self.get_credit_amount(self.batches)

        self.control = FileControl(
            batch_count, block_count, entadd_count,
            entry_hash, debit_amount, credit_amount
        )

    def get_block_count(self, batches):

        return int(math.ceil(self.get_lines(batches) / 10.0))

    def get_lines(self, batches):
        header_count = 1
        control_count = 1
        batch_header_count = len(batches)
        batch_footer_count = batch_header_count

        entadd_count = self.get_entadd_count(batches)

        lines = header_count + control_count + batch_header_count \
            + batch_footer_count + entadd_count

        return lines

    def get_entadd_count(self, batches):
        entadd_count = 0

        for batch in batches:
            entadd_count = entadd_count + int(batch.batch_control.entadd_count)

        return entadd_count

    def get_entry_hash(self, batches):
        entry_hash = 0

        for batch in batches:
            entry_hash = entry_hash + int(batch.batch_control.entry_hash)

        if len(str(entry_hash)) > 10:
            pos = len(str(entry_hash)) - 10
            entry_hash = str(entry_hash)[pos:]
        else:
            entry_hash = str(entry_hash)

        return entry_hash

    def get_debit_amount(self, batches):
        debit_amount = 0

        for batch in batches:
            debit_amount = debit_amount + int(batch.batch_control.debit_amount)

        return debit_amount

    def get_credit_amount(self, batches):
        credit_amount = 0

        for batch in batches:
            credit_amount = credit_amount + \
                int(batch.batch_control.credit_amount)

        return credit_amount

    def get_nines(self, rows, line_ending):
        nines = ''

        for i in range(rows):
            nines += '9'*94
            if i == rows - 1:
                continue
            nines += line_ending

        return nines

    def get_entry_desc(self, std_ent_cls_code):

        if std_ent_cls_code == 'PPD':
            entry_desc = 'PAYROLL'
        elif std_ent_cls_code == 'CCD':
            entry_desc = 'DUES'
        else:
            entry_desc = 'OTHER'

        return entry_desc

    def render_to_string(self, force_crlf=False):
        """
        Renders a nacha file as a string
        """
        line_ending = "\n"
        if force_crlf:
            line_ending = "\r\n"

        ret_string = self.header.get_row() + line_ending

        for batch in self.batches:
            ret_string += batch.render_to_string(force_crlf=force_crlf)

        ret_string += self.control.get_row() + line_ending

        lines = self.get_lines(self.batches)

        nine_lines = int(round(10 * (math.ceil(lines / 10.0) - (lines / 10.0))))

        ret_string += self.get_nines(nine_lines, line_ending)

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

        entadd_count = 0

        self.batch_header = batch_header
        self.entries = []

        for entry, addenda in entries:
            entadd_count += 1
            entadd_count += len(addenda)
            self.entries.append(FileEntry(entry, addenda))

        #set up batch_control

        batch_control = BatchControl(self.batch_header.serv_cls_code)

        batch_control.entadd_count = entadd_count
        batch_control.entry_hash = self.get_entry_hash(self.entries)
        batch_control.debit_amount = self.get_debit_amount(self.entries)
        batch_control.credit_amount = self.get_credit_amount(self.entries)
        batch_control.company_id = self.batch_header.company_id
        batch_control.orig_dfi_id = self.batch_header.orig_dfi_id
        batch_control.batch_id = self.batch_header.batch_id

        self.batch_control = batch_control

    def get_entry_hash(self, entries):

        entry_hash = 0

        for entry in entries:
            entry_hash += int(entry.entry_detail.recv_dfi_id[:8])

        if len(str(entry_hash)) > 10:
            pos = len(str(entry_hash)) - 10
            entry_hash = str(entry_hash)[pos:]
        else:
            entry_hash = str(entry_hash)

        return entry_hash

    def get_debit_amount(self, entries):
        debit_amount = 0

        for entry in entries:
            if str(entry.entry_detail.transaction_code) in \
                    ['27', '37', '28', '38']:
                debit_amount = debit_amount + int(entry.entry_detail.amount)

        return debit_amount

    def get_credit_amount(self, entries):
        credit_amount = 0

        for entry in entries:
            if str(entry.entry_detail.transaction_code) in \
                    ['22', '32', '23', '33']:
                credit_amount += int(entry.entry_detail.amount)

        return credit_amount

    def render_to_string(self, force_crlf=False):
        """
        Renders a nacha file batch to string
        """
        line_ending = "\n"
        if force_crlf:
            line_ending = "\r\n"

        ret_string = self.batch_header.get_row() + line_ending

        for entry in self.entries:
            ret_string += entry.render_to_string(force_crlf=force_crlf)

        ret_string += self.batch_control.get_row() + line_ending

        return ret_string


class FileEntry(object):
    """
    Holds:

    EntryDetail (1)
    AddendaRecord (n) <-- for some types of entries there can be more than one
    """

    def __init__(self, entry_detail, addenda_record=[]):
        """
        args: entry_detail( EntryDetail), addenda_record (List[AddendaRecord])
        """

        self.entry_detail = entry_detail
        self.addenda_record = []

        for index, addenda in enumerate(addenda_record):
            self.addenda_record.append(
                AddendaRecord(
                    self.entry_detail.std_ent_cls_code,
                    pmt_rel_info=addenda.get('payment_related_info').upper(),
                    add_seq_num=index + 1,
                    ent_det_seq_num=entry_detail.trace_num[-7:]
                )
            )

        if self.addenda_record:
            self.entry_detail.add_rec_ind = 1

    def render_to_string(self, force_crlf=False):
        """
        Renders a nacha batch entry and addenda to string
        """
        line_ending = "\n"
        if force_crlf:
            line_ending = "\r\n"

        ret_string = self.entry_detail.get_row() + line_ending

        for addenda in self.addenda_record:
            ret_string += addenda.get_row() + line_ending

        return ret_string
