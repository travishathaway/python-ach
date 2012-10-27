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

    def __init__(self, header, batches, control ):
        """
        args: header (Header), batches (List[FileBatch]), control (FileControl)
        """

        self.header  = header
        self.batches = batches
        self.control = control

    def render_to_string(self):
        """
        Renders a nacha file as a string
        """

        ret_string = self.header.get_row() + "\n"

        for batch in batches:
            ret_string += batch.render_to_string

        ret_string += self.control.get_row()

        return ret_string

class FileBatch(object):

    """
    Holds:

    BatchHeader  (1)
    Entry        (n) <-- multiple
    BatchControl (1)
    """

    def __init__(self, batch_header, entries, batch_control):
        """
        args: batch_header (BatchHeader), entries (List[FileEntry]), batch_control (BatchControl)
        """

        self.batch_header   = batch_header
        self.entries        = entries
        self.batch_control  = batch_control


    def render_to_string(self):
        """
        Renders a nacha file batch to string
        """

        ret_string = self.batch_header + "\n"

        for entry in entries:
            ret_string += self.entries.render_to_string()

        ret_string += self.batch_control + "\n"

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
