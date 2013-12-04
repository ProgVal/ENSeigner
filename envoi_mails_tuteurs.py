#!/usr/bin/env python3
# -*- coding: utf8 -*-

from envoi_mails_commun import *

tuteurs = get_contacts(contacts)

with people as fd:
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
        for entree_global in tuteurs:
            if not entree_global['First Name']:
                continue
            combinaisons = make_combinaisons(entree_global)
            name = (entree_seance['Nom'], entree_seance['Prénom'])
            if name in combinaisons:
                lists[0].append((0, ' '.join(name), entree_global['E-mail Address']))
                found = True
        if not found:
            lists[1].append(entree_seance)

with cgi_capture():
    print()
    print('Confirmation :')
    sys.stdout.write('\t')
    for confirm in confirms:
        print_email(confirm)
    print()
    print()
    print('Échecs confirmation :')
    for fail in confirm_fails:
        print('\t' + str(fail))
    print()
    print('Non-confirmation :')
    sys.stdout.write('\t')
    for abort in aborts:
        print_email(abort)
    print()
    print()
    print('Échecs non-confirmation :')
    for fail in abort_fails:
        print('\t' + str(fail))
    print()
    print('État de confirmation inconnu :')
    for fail in fails:
        print('\t' + str(fail))

