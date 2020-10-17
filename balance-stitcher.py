import glob
import os

from tika import parser
from html.parser import HTMLParser
from PyPDF2 import PdfFileWriter, PdfFileReader

output = PdfFileWriter()

class MyHTMLParser(HTMLParser):

   balanceFound = False

   withinDiv = False
   currentPageNumber = 0
   balanceFoundAtPageNumber = -1

   currentText = ""

   #HTML Parser Methods - Stax inspired
   def handle_starttag(self, startTag, attrs):
       if startTag == "div":
            self.currentPageNumber = self.currentPageNumber + 1
            self.withinDiv = True
            self.currentText = ""

   def handle_endtag(self, endTag):
       if endTag == "div" and self.withinDiv:
           if self.currentText.find("Balance") != -1 and self.balanceFoundAtPageNumber == -1:
               self.balanceFoundAtPageNumber = self.currentPageNumber
               self.withinDiv = False
               self.currentText = ""

   def handle_data(self,data):
       if self.withinDiv:
            self.currentText += data

for pdf in sorted(glob.glob("C:\\balancemerger\\statements\\*.pdf"), key=os.path.getmtime):
    print("" + pdf)
    parsed = parser.from_file(pdf, xmlContent=True)

    xhtml_content = parsed["content"]
    xhtml_content_ascii = ''.join([i if ord(i) < 128 else ' ' for i in xhtml_content])

    # creating an object of the overridden class
    myParser = MyHTMLParser()

    # Feeding the content
    myParser.feed(xhtml_content_ascii)

    print("Balance page is ", myParser.balanceFoundAtPageNumber)

    if myParser.balanceFoundAtPageNumber != -1:
        infile = PdfFileReader(pdf, 'rb')
        if infile.isEncrypted:
            infile.decrypt("")
        balance_present_page = infile.getPage(myParser.balanceFoundAtPageNumber - 1)
        output.addPage(balance_present_page)
    else:
        print("Balance not found in file : " + pdf)

with open('C:\\balancemerger\\output\\Balance-present-pages-alone.pdf', 'wb') as f:
    output.write(f)
