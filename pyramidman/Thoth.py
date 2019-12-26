
from docx import Document
from docx.shared import Inches

import pandas as pd
import datetime as dt
import os

from typing import List
# Creare new Word Document


class Papyrus():
    """Class to generate a report for the meetings assisted by pyradmidman.
    """

    def __init__(self, title: str = "pyramidman presentation", report_type: str = "meeting",
                 date: str = None, attendants: List[str] = None):
        # Main report information
        self.title = title
        self.report_type = report_type
        if date is None:
            self.date = str(dt.datetime.now())
        else:
            self.date = date

        self.attendants = attendants

        # Initialize some data structures
        self.document = None

        # Hardcoded param:
        self.logo_filepath = "../img/pyramidman_logo2.png"

    def add_table_from_df(self, df):
        """It creates and adds a table to the document from a pandas table
        """
        nrows, ncols = df.shape
        columns = df.columns.values
        table = self.document.add_table(rows=nrows+1, cols=ncols)

        header_cells = table.rows[0].cells
        i = 0
        for col in columns:
            header_cells[i] = col
            i += 1

        for i in range(nrows):
            row_cells = table.add_row().cells

            for j in range(ncols):
                row_cells[j].text = str(df.iloc[i][columns[i]])

    def add_first_page(self):

        ######################## FIRST PAGE #####################
        # Add pyramidman logo
        self.document.add_picture(self.logo_filepath, width=Inches(3.0))
        self.document.add_heading('Meeting ', level=0)

        p = self.document.add_paragraph()

        # Now we add different texts of the first paragraph.
        text = 'This document contains the information regarding the meeting'
        p.add_run(text)
        text = self.title + " "
        p.add_run(text).bold = True

        text = "carried on the day "
        p.add_run(text)
        initial_text = str(self.date) + " "
        p.add_run(initial_text).bold = True

        text = "The attendants to the meeting were: "
        if self.attendants is not None:
            for i in range(len(self.attendants)):
                text += self.attendants[i]
                if i < len(self.attendants)-1:
                    text += ", "

        p.add_run(text)

        self.document.add_page_break()

    def create_document(self, filepath='presentation.docx'):
        # This function will create the document, assuming all the data is loaded

        # Create word document
        document = Document()
        self.document = document
        
        self.add_first_page()
        # Create Initial text describing the document

#        document.add_paragraph(
#            'first item in unordered list', style='ListBullet'
#        )
#        document.add_paragraph(
#            'first item in ordered list', style='ListNumber'
#        )

        ############ Summary of the cleaning #########
        # State how the process went in general, like
        """
        Duration, did it meet the FDA requirements ? Warnings issued ? 
        """

        ############ SECOND PAGE: Cleaning Process Report #########
        document.add_heading('Cleaning Report', level=1)

        # Save document in the end
        document.save(filepath)
        os.system("chmod 777 " + filepath)
