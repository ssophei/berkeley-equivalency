from pdfgrabber import PDFGrabber
from databasemaker import DatabaseMaker


def main():
    grabber = PDFGrabber(79, 'Computer Science, B.A.', 'CS', 0.2)
    id_to_key = grabber.get_pdfs()
    maker = DatabaseMaker('UC Berkeley', 'CS', id_to_key)
    maker.add_classes()


if __name__ == '__main__':
    main()
