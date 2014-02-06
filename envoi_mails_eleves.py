#!/usr/bin/env python3
# -*- coding: utf8 -*-

from envoi_mails_commun import *

with cgi_capture():
    eleves = get_contacts(contacts)

    with people as fd:
        seance = list(csv.reader(fd, delimiter=','))
        headers = seance[0]
        fixed_headers = list()
        for header in headers:
            while header in fixed_headers:
                header += '_'
            fixed_headers.append(header)
        headers = fixed_headers
        seance = map(lambda x:dict(zip(headers, map(normalize, x))), seance[1:])
        fails = []
        confirms = []
        confirm_fails = []
        aborts = []
        abort_fails = []
        for entree_seance in seance:
            if not entree_seance['Nom']:
                continue
            if 'confirmation' not in list(map(normalize, headers)) or \
                    entree_seance['confirmation'] == 'oui':
                lists = (confirms, confirm_fails)
            elif entree_seance['confirmation'] == 'non':
                lists = (aborts, abort_fails)
            elif entree_seance['confirmation'] == 'doublon':
                pass
            else:
                lists = (fails, fails)
            best_match = None
            for entree_global in eleves:
                if not entree_global['First Name']:
                    continue
                combinaisons = make_combinaisons(entree_global)
                name = (entree_seance['Nom'], entree_seance['Prénom'])
                if name in combinaisons:
                    best_match = (0, ' '.join(name), entree_global['E-mail Address'])
            if not best_match:
                for entree_global in eleves:
                    if not entree_global['First Name']:
                        continue
                    combinaisons = make_combinaisons(entree_global)
                    nom = (entree_seance['Nom'], entree_seance['Prénom'])
                    delta = min(map(functools.partial(distance2, nom), combinaisons))
                    assert delta != 0
                    if not best_match or (delta < best_match[0]):
                        best_match = (delta, ' '.join(nom), entree_global['E-mail Address'])
            if best_match and best_match[0] < 3:
                lists[0].append(best_match)
            else:
                lists[1].append(entree_seance)

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
