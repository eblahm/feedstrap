import csv
from goose import Goose
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
import urllib2

def convert_pdf(path):

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str


def ps(x):
    try:
        return str(x)
    except:
        try:
            x.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
        except:
            return x.encode('ascii', 'xmlcharrefreplace')
#g = Goose()

new_csv = file('/Users/Matt/Dropbox/dev/ssg_site/feedstrap/seed_data/resources2.csv', 'wb')
csv_writer = csv.writer(new_csv)
article_extract_retry = 0
new_extracted_article = 0
error = 0
with open('/Users/Matt/Dropbox/dev/ssg_site/feedstrap/seed_data/resources.csv', 'rb') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row[5].strip()[-3:] == 'pdf':
            print "Trying... " + row[4]
            print row[5]
            try:
                article_extract_retry += 1
                article_page = urllib2.urlopen(row[5])
                pdf_data = article_page.read()
                fn = '/Users/Matt/Desktop/pdfs/' + row[4]
                new_file = open(fn, 'wb')
                new_file.write(pdf_data)
                new_file.close()
                row[8] = convert_pdf(fn)
            except:
                error += 1
        if len(row[8]) < 20:
            article_extract_retry += 1
            try:
                article = g.extract(url=row[5])
                row[8] = ps(article.cleaned_text)
            except:
                print ps(row[4])[:20]
                error += 1
            if len(row[8]) > 20:
                new_extracted_article += 1
        csv_writer.writerow(row)
new_csv.close()

print "# errors = %i" % (error)
print "# retried = %i" % (article_extract_retry)
print "# extracted = %i" % (new_extracted_article)
print "improvment rate = %.5f" % (new_extracted_article / float(article_extract_retry))

