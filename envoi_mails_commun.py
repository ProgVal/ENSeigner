# -*- coding: utf8 -*-

import os
import io
import csv
import sys
import cgi
import codecs
import functools

CGI_MODE = 'GATEWAY_INTERFACE' in os.environ

def normalize(x):
    return x.lower().replace(' ', '').replace('é', 'e').replace('è', 'e') \
            .replace('\'', '').replace('ï', 'i')

def distance(s, t):
    """Returns the levenshtein edit distance between two strings."""
    n = len(s)
    m = len(t)
    if n == 0:
        return m
    elif m == 0:
        return n
    d = []
    for i in range(n+1):
        d.append([])
        for j in range(m+1):
            d[i].append(0)
            d[0][j] = j
        d[i][0] = i
    for i in range(1, n+1):
        cs = s[i-1]
        for j in range(1, m+1):
            ct = t[j-1]
            cost = int(cs != ct)
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+cost)
    return d[n][m]

def distance2(x, y):
    if not all([x[0], x[1], y[0], y[1]]):
        return 10000
    return distance(x[0], y[0]) + distance(x[1], y[1])

def make_combinaisons(entree_global):
    return (
            (entree_global['Middle Name'], entree_global['First Name']),
            (entree_global['First Name'], entree_global['Middle Name']),
            (entree_global['Last Name'], entree_global['First Name']),
            (entree_global['First Name'], entree_global['Last Name']),
            (entree_global['First Name'], entree_global['Middle Name']+entree_global['Last Name']),
            (entree_global['Middle Name']+entree_global['Last Name'], entree_global['First Name'])
            )

def get_contacts(fd):
    people = list(csv.reader(fd, delimiter=','))
    headers = people[0]
    people = list(map(lambda x:dict(zip(headers, map(normalize, x))), people[1:]))
    return people

def print_email(match):
    sys.stdout.write('%s <%s>, ' % (match[1], match[2]))
    sys.stdout.flush()

def cgi_write(txt, html=False):
    writer = codecs.getwriter('utf8')(sys.stdout.buffer)

    mime = 'html' if html else 'plain'
    writer.write('Content-type: text/%s; charset=utf8\r\n' % mime)
    writer.write('Content-length: %i\r\n' % len(txt.encode()))
    writer.write('\r\n')
    writer.write(txt)

if CGI_MODE:
    class CgiCapture:
        def __init__(self):
            pass
        def __enter__(self):
            self._stdout = sys.stdout
            sys.stdout = io.StringIO()
        def __exit__(self, *args):
            (sys.stdout, stringio) = (self._stdout, sys.stdout)
            stringio.seek(0)
            cgi_write(stringio.read())
else:
    class CgiCapture:
        def __init__(self):
            pass
        def __enter__(self):
            pass
        def __exit__(self, *args):
            pass
def cgi_capture():
    return CgiCapture()

if CGI_MODE:
    form = cgi.FieldStorage()
    if 'contacts' in form:
        assert 'people' in form
        contacts = io.StringIO(form['contacts'].file.read().decode('latin1'))
        people = io.StringIO(form['people'].file.read().decode())
    else:
        cgi_write("""<html><head></head><body>
            <form action="" method="post" enctype="multipart/form-data">
            <label for="contacts">Fichier contacts</label> 
            <input type="file" name="contacts" id="contacts" />
            (Pour obtenir le fichier, aller dans<a href="https://mail.google.com/mail/u/0/?tab=om#contacts">les contacts Gmail</a>, cliquer sur « Plus », puis « Exporter », cocher « Format CSV Outlook »)
            <br />
            <br />
            <label for="people">Fichier des présent(e)s</label>
            <input type="file" name="people" id="people" />
            (Pour obtenir le fichier, aller dans <a href="https://drive.google.com/">les Google Drive</a>, cliquer sur le fichier de réponses, puis « File », puis « Download as » et « Comma Separated Values »)
            <br />
            <br />
            <input type="submit" value="Envoi" />
            </form></body></html>""", True)
else:
    if len(sys.argv) != 3:
        print('Syntaxe : envoi_mails_eleves.py fichier_contacts.csv fichier_personnes_seance.csv')
        exit(1)
    else:
        contacts = open(sys.argv[1], 'r', encoding='latin1')
        people = open(sys.argv[2])
