from pdfgrabber import PDFGrabber
from databasemaker import DatabaseMaker
school_id = 79
school_name = 'University of California, Berkeley'
major = 'Statistics, B.A.'
nickname = 'Statistics'
delay = 0.5
grabber = PDFGrabber(school_id, major, nickname, delay)
print('getting pdfs...')
id_to_key = grabber.get_pdfs()
# maker = DatabaseMaker(school_name, nickname, id_to_key)
# maker.add_classes()
