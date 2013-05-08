import csv
from goose import Goose


def ps(x):
    try:
        return str(x)
    except:
        try:
            x.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
        except:
            return x.encode('ascii', 'xmlcharrefreplace')
g = Goose()
new_csv = file('/Users/Matt/Desktop/resources_improved.csv', 'wb')
csv_writer = csv.writer(new_csv)
article_extract_retry = 0
new_extracted_article = 0
error = 0
with open('/Users/Matt/Desktop/resources.csv', 'rb') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
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
