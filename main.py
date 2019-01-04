#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import textwrap
import io
import os
import datetime

import sys

# Avoid warning
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


# PDF Layout stuff
def get_pdf_width_and_heigth():
    return(A4)

def get_pdf_width():
    return(get_pdf_width_and_heigth()[0])

def get_pdf_heigth():
    return(get_pdf_width_and_heigth()[1])

num_rows = 5 # Rows of cards inside the pdf
num_columns = 4 # Number of cards per row inside the pdf
cards_per_page = num_columns*num_rows

width_margin = get_pdf_width()/30 # Empty space on the left
height_margin = get_pdf_heigth()/27 # Empty space above
block_size = (get_pdf_width()-2*width_margin)/num_columns + get_pdf_width()/142

font_size = 12


def text_centered_position(index):
    "Return text position inside an one page pdf"
    index = (cards_per_page-index-1)
    if (index >= 0 and index < cards_per_page):
        index_pos = (int(index/num_columns), index%num_columns)
        width = width_margin + block_size*index_pos[1] + block_size/2
        height = height_margin + block_size*index_pos[0] + block_size/2 + block_size/25
        
        return (width, height)
    else:
        return(None)

def split_text(text):
    "Split text in several lines"
    # TODO: Be careful if just one word is splited
    return(textwrap.wrap(text, width=18))

def write_text_to_pdf (text, index, canvas):
    "Draw text inside a pdf using canvas"
    splited_text = split_text(text)
    space_between_lines = block_size/7

    for i in range(len(splited_text)):
        offset = i - len(splited_text)/2
        if (text_centered_position(index) != None):
            width  = text_centered_position(index)[0]
            height = text_centered_position(index)[1] - offset*space_between_lines
            canvas.drawCentredString(width, height, splited_text[i]
            )


black_cards_dir = "./Input/BlackCards/"
white_cards_dir = "./Input/WhiteCards/"

packet = io.BytesIO()

# Create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=A4)
can.setFont('Helvetica-Bold', font_size)



pdf_page_index = 0
card_index = 0 # Index inside one pdf page

# Black cards
# black_card_text_color = colors.white
# can.setFillColor(black_card_text_color)
for filename in os.listdir(black_cards_dir):
    path = black_cards_dir + filename
    file_reader = open(path, "r")

    for line in file_reader:
        write_text_to_pdf(line, card_index, can)
        card_index += 1

        if (card_index == cards_per_page):
            card_index = 0
            pdf_page_index += 1
            can.showPage()
            can.setFont('Helvetica-Bold', font_size)

if (card_index > 0):
    can.showPage()
    can.setFont('Helvetica-Bold', font_size)
    pdf_page_index += 1
    card_index = 0
    
num_black_pages = pdf_page_index

# White cards
for filename in os.listdir(white_cards_dir):
    path = white_cards_dir + filename
    file_reader = open(path, "r")

    for line in file_reader:
        write_text_to_pdf(line, card_index, can)
        card_index += 1

        if (card_index == cards_per_page):
            card_index = 0
            pdf_page_index += 1
            can.showPage()
            can.setFont('Helvetica-Bold', font_size)

        
can.showPage()
can.save()

# Add the watermarks and create final pdf
new_pdf = PdfFileReader(packet)
output = PdfFileWriter()

for i in range(pdf_page_index):
    existing_pdf = None
    if (i < num_black_pages):
        existing_pdf = PdfFileReader(open("./Input/CAH_BlankBlackCards.pdf", "rb"))
    else:
        existing_pdf = PdfFileReader(open("./Input/CAH_BlankWhiteCards.pdf", "rb"))

    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(i))
    output.addPage(page)

# Finally, write "output" to a real file
output_file_name = "./Output/Cards-" + str(datetime.date.today()) + ".pdf"
outputStream = open(output_file_name, "wb")
output.write(outputStream)
outputStream.close()