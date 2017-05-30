from hashlib import sha1
from rdflib import URIRef
from modules.turtleGrapher.turtle_utils import generate_uri as gu

def test_generate_uri():
    # test generate usage:
    e = URIRef(u'http://www.biointerchange.org/gfvo#Contig')
    r = gu('g:Contig')
    assert r == e

    # test spfyid generation (ie. root namespace)
    e = URIRef(u'https://www.github.com/superphy#spfy1')
    r = gu(':spfy1')
    assert r == e

    # test cases where you call gu() with and existing URIRef and want to
    # append something
    # ex. gu(uriGenome, "/contigs") in datastruct_savvy.py
    # e was previously generated
    e = URIRef(u'https://www.github.com/superphy#1947b0815e6c1b11565e1ef5db9c884e3eead520/contigs')
    # mock_filehash mocks the hash of a genome file
    mock_filehash = sha1('thisvaluedoesntmatterfornow').hexdigest()
    # generate the mock uriGenome
    # this returns a rdflib.URIRef object
    mock_uriGenome = gu(':' + mock_filehash)
    # this is the test case, r is a mock uriContigs
    r = gu(mock_uriGenome, '/contigs')
    assert r == e

    # test with a url in the form of a string
    e = URIREF('https://www.github.com/superphy#')
    r = gu('https://www.github.com/superphy#')
    assert r == e
