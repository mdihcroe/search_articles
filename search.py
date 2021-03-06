from Bio import Entrez
import xml.etree.ElementTree as ET
import time
from pathlib import Path


def not_checked(id):
    hist_file = 'ids_checked.txt'
    if Path(hist_file).is_file() and id not in open(hist_file).read():
        return True
    else:
        return False


def main():
    Entrez.email = "elizarova@phystech.edu"

    key_words = '[[ [ seawater OR marine OR sediment OR freshwater OR ocean OR river OR lake OR aquatic] ' \
                'metagenome ] OR [ marine microbial community ]] NOT gut] NOT intestine] NOT human'

    # get number of results
    handle = Entrez.esearch(db="bioproject", term=key_words)
    record = Entrez.read(handle)
    handle.close()

    # retrieve all results
    handle = Entrez.esearch(db="bioproject", term=key_words, retmax=record['Count'])
    record = Entrez.read(handle)
    handle.close()

    number_of_projects = len(record['IdList'])
    print 'Number of projects to be checked: ', number_of_projects

    for id in record['IdList']:
        print 'Bioproject id: ', id

        try:
            if not_checked(id):  # not to check same articles again if e.g. there are changes in key_words

                # get bioproject id
                handle = Entrez.efetch(db="bioproject", id=id, retmode='xml')
                record = handle.read()
                handle.close()

                root = ET.fromstring(record)
                project_accession = root.findall('.//ArchiveID')[0].attrib['accession']
                print 'Bioproject accession number: ', project_accession

                # check if related to any article in db_name
                db_name = "pmc"

                handle = Entrez.esearch(db=db_name, term=project_accession)
                record = handle.read()
                handle.close()

                root = ET.fromstring(record)
                number_of_articles = int(root[0].text)

                if number_of_articles != 0:
                    id_article = root.findall('.//IdList/Id')[0].text
                    print 'ARTICLE FOUND:', id_article

                    # get article info
                    handle = Entrez.efetch(db=db_name, id=id_article, retmode='xml')
                    record = handle.read()
                    handle.close()

                    root = ET.fromstring(record)

                    title = root.findall('.//title-group/article-title')[0].text
                    abstract = root.findall('.//abstract/p')[0].text

                    txt = open("Output.txt", "a")
                    txt.write('%s\n%s id: %s\nTITLE: %s\nABSTRACT:\n%s\n\n' %
                              (project_accession, db_name, id_article, title, abstract))
                    txt.close()

                # save txt with project ids which have been checked
                f = open('ids_checked.txt', 'a')
                f.write('%s\n' % id)
                f.close()
                time.sleep(1)  # NCBI can kick you out if too many requests in a row

        except Exception:
            print 'error'
            txt = open("Error", "a")
            txt.write('%s\n' % id)
            txt.close()

        number_of_projects -= 1
        print 'Number of projects to be checked left: %s\n_' % number_of_projects


if __name__ == "__main__":
    main()
