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

def distance(s, t, deletion_cost=1):
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
            d[i][j] = min(d[i-1][j]+deletion_cost, d[i][j-1]+deletion_cost, d[i-1][j-1]+cost)
    return d[n][m]

def read_csv(fd, handle_confirms=False, normalize_=True):
    entries = list(csv.reader(fd, delimiter=','))
    headers = entries[0]
    fixed_headers = list()
    for header in headers:
        while header in fixed_headers:
            header += '_'
        fixed_headers.append(header)
    headers = fixed_headers
    if normalize_:
        entries = map(lambda x:dict(zip(headers, map(normalize, x))), entries[1:])
    else:
        entries = map(lambda x:dict(zip(headers, x)), entries[1:])
    if handle_confirms and 'confirmation' in headers:
        entries = map(lambda x:x['confirmation'] == 'oui', entries)
    entries = list(entries)
    for entry in entries:
        for (key, value) in list(entry.items()):
            entry[key.lower()] = value
    return (headers, entries)

def collect_extra_debug_data():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    data = ''
    try:
        tb = sys.exc_info()[2]
        stack = []

        while tb:
            stack.append(tb.tb_frame)
            tb = tb.tb_next
    finally:
        del tb

    data += 'Locals by frame, innermost last:\n'
    for frame in stack:
        data += '\n\n'
        data += ('Frame %s in %s at line %s\n' % (frame.f_code.co_name,
                                             frame.f_code.co_filename,
                                             frame.f_lineno))
        frame_locals = frame.f_locals
        for inspected in ('self', 'cls'):
            if inspected in frame_locals:
                if hasattr(frame_locals[inspected], '__dict__') and \
                        frame_locals[inspected].__dict__:
                    for (key, value) in frame_locals[inspected].__dict__.items():
                        frame_locals['%s.%s' % (inspected, key)] = value
        for key, value in frame_locals.items():
            if key == '__builtins__':
                # This is flooding
                continue
            data += ('\t%20s = ' % key)
            #We have to be careful not to cause a new error in our error
            #printer! Calling str() on an unknown object could cause an
            #error we don't want.
            try:
                data += repr(value) + '\n'
            except:
                data += '<ERROR WHILE PRINTING VALUE>\n'
    data += '\n'
    data += '+-----------------------+\n'
    data += '| End of locals display |\n'
    data += '+-----------------------+\n'
    data += '\n'
    return data

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
    import traceback
    class CgiCapture:
        def __init__(self):
            pass
        def __enter__(self):
            self._stdout = sys.stdout
            self._stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
        def __exit__(self, e_typ, e_val, trcbak):
            if e_val:
                print('Erreur.\n')
            (sys.stdout, sys.stderr, stringio) = (self._stdout, self._stderr, sys.stdout)
            if e_val:
                traceback.print_tb(trcbak, None, stringio)
                stringio.write(repr(e_val))
                stringio.write('\n')
                stringio.write(collect_extra_debug_data())
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

if CGI_MODE and RUN_MAIN:
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
            (Pour obtenir le fichier, aller dans <a href="https://mail.google.com/mail/u/0/?tab=om#contacts">les contacts Gmail</a>, cliquer sur « Plus », puis « Exporter », cocher « Format CSV Outlook »)
            <br />
            <br />
            <label for="people">Fichier des présent(e)s</label>
            <input type="file" name="people" id="people" />
            (Pour obtenir le fichier, aller dans <a href="https://drive.google.com/">le Google Drive</a>, cliquer sur le fichier de réponses, puis « File », puis « Download as » et « Comma Separated Values »)
            <br />
            <br />
            <input type="submit" value="Envoi" />
            </form></body></html>""", True)
        exit()
elif RUN_MAIN:
    if len(sys.argv) != 3:
        print('Syntaxe : envoi_mails_eleves.py fichier_contacts.csv fichier_personnes_seance.csv')
        exit(1)
    else:
        contacts = open(sys.argv[1], 'r', encoding='latin1')
        people = open(sys.argv[2])
