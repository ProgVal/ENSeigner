#!/usr/bin/env python3

import os
import sys
import json

__builtins__.RUN_MAIN = False

from common import distance, normalize, read_csv

def print_help():
    print('h : Afficher cette aide')
    print('q : Quitter')
    print()
    print('c : Charger un état')
    print('s : Sauvegarder un état')
    print()
    print('a : Afficher l’état actuel')
    print('p : Pointer quelqu’un')
    print('e : Envoyer un groupe')

def distance_key(input_, item):
    return distance(normalize(input_), item[1], deletion_cost=0.5)
def get_name(person):
    return '%s %s' % (person['Prénom'], person['Nom'])

def display_state(tutors, students, waiting, topic=None):
    if isinstance(topic, str):
        students = filter(lambda x:get_name(x) in waiting, students)
        tutors = filter(lambda x:get_name(x) in waiting, tutors)
        print('État pour la matière « %s » :' % topic)
        print('\tTuteurs et tutrices :')
        for tutor in filter(lambda x:topic in x['Matières'].split(', '), tutors):
            print('\t\t%s %s : %s ; %s' % (tutor['Prénom'], tutor['Nom'],
                tutor['Matières'], tutor['Remarque'] if 'Remarque' in tutor else ''))
        print('\tÉlèves :')
        for student in filter(lambda x:topic == x['Matière'], students):
            print('\t\t%s %s ; %s' % (student['Prénom'], student['Nom'],
                student['Remarque'] if 'Remarque' in student else ''))
    else:
        assert isinstance(topic, list)
        topics = topic
        for topic in set(topics):
            display_state(tutors, students, waiting, topic)

def main(tutors, students):
    tutors = list(tutors)
    students = list(students)
    names = [(get_name(x), x, True) for x in tutors] + \
            [(get_name(x), x, False) for x in students]
    names = [(x, ' '.join(map(normalize, x.split(' '))), y, z) for (x,y,z)
             in names]
    waiting = []
    sent = []
    print_help()
    while True:
        remaining_topics = list(set(map(lambda x:x['Matière'], students)))
        action = input('Action ? ')
        if action == 'h':
            print_help()
        elif action == 'q':
            answer = input('Quitter, vraiment ? (o/n) ')
            if answer == 'o':
                return
        elif action == 'c':
            filename = input('Nom de fichier ? ')
            with open(filename, 'r') as fd:
                (tutors, students, names, waiting, sent) = json.load(fd)
                waiting = set(waiting)
        elif action == 's':
            filename = input('Nom de fichier ? ')
            try:
                os.unlink(filename)
            except:
                pass
            with open(filename, 'a') as fd:
                json.dump((tutors, students, names, waiting, sent), fd, indent=4)
        elif action == 'a':
            display_state(tutors, students, waiting, remaining_topics)
        elif action == 'p':
            name = input('Nom ? ')
            matches = sorted(names, key=lambda x:distance_key(name, x))
            for (i, item) in enumerate(matches[0:9]):
                print('%i) %s' % (i+1, item[0]))
            print('0) Aucune correspondance')
            print()
            id_ = int(input('Numéro ? '))
            if not id_:
                continue
            id_-=1
            (name, _, person, is_tutor) = matches[id_]
            if is_tutor:
                topic = person['Matières']
            else:
                topic = person['Matière']
            if 'Remarque' in person:
                print('Nom : %s, matière(s) : %s, remarque : %s' %
                        (name, topic, person['Remarque']))
            else:
                print('Nom : %s, matière(s) : %s' % (name, topic))
            confirmation = None
            while confirmation not in ('o', 'n'):
                confirmation = input('Confirmation ? (o/n) ')
            if confirmation == 'n':
                continue
            waiting.append(get_name(person))
            display_state(tutors, students, waiting, topic)
        elif action == 'e':
            for (i, topic) in enumerate(remaining_topics):
                print('%.2i) %s' % (i+1, topic))
            print('00) Aucune correspondance')
            id_ = int(input('Numéro ? '))
            if not id_:
                continue
            id_-=1
            topic = remaining_topics[id_]
            print('Personnes non affectées :')
            browsing_tutors = False
            persons = sorted(filter(lambda x:x[0] in waiting, names),
                    key=lambda x:not x[3])
            for (i, (name, _, person, is_tutor)) in enumerate(persons):
                if 'Matières' in person and \
                        topic not in person['Matières'].split(' '):
                    continue
                if 'Matière' in person and topic != person['Matière']:
                    continue
                if not browsing_tutors and is_tutor:
                    print('\tTuteurs et tutrices :')
                    browsing_tutors = True
                if browsing_tutors and not is_tutor:
                    print('\tÉlèves :')
                print('\t\t%.02i) %s' % (i+1, name))
            ids = input('Numéros ? (séparés par des espaces) ')
            for id_ in ids.split(' '):
                if not id_:
                    continue
                person = persons[int(id_)-1]
                waiting.remove(person[0])
                if person[3]:
                    tutors.remove(person[2])
                else:
                    students.remove(person[2])
                sent.append(person)
        else:
            print('Action inconnue.')




if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Syntax: %s tutors.csv students.csv' % sys.argv[0])
        exit()
    with open(sys.argv[1]) as tutors:
        with open(sys.argv[2]) as students:
            main(read_csv(tutors, True, False), read_csv(students, True, False))

