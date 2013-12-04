#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import sys

if len(sys.argv) != 3:
    print('Syntaxe : envoi_mails_eleves.py fichier_contacts.csv fichier_eleves_seance.csv')
    exit(1)

def normalize(x):
    return x.lower().replace(' ', '').replace('é', 'e').replace('è', 'e')

with open(sys.argv[1], 'r', encoding='latin1') as fd:
    eleves = list(csv.reader(fd, delimiter=','))
    headers = eleves[0]
    eleves = list(map(lambda x:dict(zip(headers, map(normalize, x))), eleves[1:]))

with open(sys.argv[2]) as fd:
    seance = list(csv.reader(fd, delimiter=','))
    headers = seance[0]
    seance = map(lambda x:dict(zip(headers, map(normalize, x))), seance[1:])
    fails = []
    confirms = []
    confirm_fails = []
    aborts = []
    abort_fails = []
    for entree_seance in seance:
        if not entree_seance['Nom']:
            continue
        if entree_seance['confirmation'] == 'oui':
            lists = (confirms, confirm_fails)
        elif entree_seance['confirmation'] == 'non':
            lists = (aborts, abort_fails)
        else:
            lists = (fails, fails)
        found = False
        for entree_global in eleves:
            if not entree_global['First Name']:
                continue
            if (entree_seance['Nom'], entree_seance['Prénom']) in (
                    (entree_global['Middle Name'], entree_global['First Name']),
                    (entree_global['First Name'], entree_global['Middle Name']),
                    (entree_global['Last Name'], entree_global['First Name']),
                    (entree_global['First Name'], entree_global['Last Name'])
                    ):
                lists[0].append(entree_global['E-mail Address'])
                found = True
        if not found:
            lists[1].append(entree_seance)
    print()
    print('Confirmation :')
    sys.stdout.write('\t')
    for confirm in confirms:
        sys.stdout.write(confirm)
        sys.stdout.write(', ')
    print()
    print()
    print('Échecs confirmation :')
    for fail in confirm_fails:
        print('\t' + str(fail))
    print()
    print('Non-confirmation :')
    sys.stdout.write('\t')
    for abort in aborts:
        sys.stdout.write(abort)
        sys.stdout.write(', ')
    print()
    print()
    print('Échecs non-confirmation :')
    for fail in abort_fails:
        print('\t' + str(fail))
    print()
    print('État de confirmation inconnu :')
    for fail in fails:
        print('\t' + str(fail))


print()
