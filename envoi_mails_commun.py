# -*- coding: utf8 -*-

import csv
import sys
import functools

if len(sys.argv) != 3:
    print('Syntaxe : envoi_mails_eleves.py fichier_contacts.csv fichier_eleves_seance.csv')
    exit(1)

def normalize(x):
    return x.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')

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

def get_contacts(filename):
    with open(sys.argv[1], 'r', encoding='latin1') as fd:
        people = list(csv.reader(fd, delimiter=','))
        headers = people[0]
        people = list(map(lambda x:dict(zip(headers, map(normalize, x))), people[1:]))
        return people

def print_email(match):
    sys.stdout.write('%s <%s>, ' % (match[1], match[2]))
    sys.stdout.flush()
