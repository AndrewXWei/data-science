# encoding=utf8
"""
crawling the courses list in udacity
"""
from bs4 import BeautifulSoup
import requests
import json
udacity_baseurl = 'https://www.udacity.com'
html_doc = requests.get(udacity_baseurl + '/courses/all').text
soup = BeautifulSoup(html_doc, 'html.parser')
outfile1 = open('./udacity_course_list_json.txt', 'w')
outfile2 = open('./udacity_course_list_text.txt', 'w')
for t in soup.find_all('div', 'course-summary-card'):
    datadict = {}
    title = t.select_one('a.capitalize').get_text().strip()
    href = udacity_baseurl + t.select_one('a')['href']
    school = ''
    try:
        school = t.select_one('h4.category').get_text().strip()
    except BaseException:
        pass

    skills = []
    collaboration = []
    try:
        class_list = t.select_one('div.right-sub').select_one('div')['class']
        if 'level' not in class_list:
            for s in t.select_one(
                    'div.right-sub').select_one('div').find_all('span'):
                if 'skills' in class_list:
                    skills.append(
                        s.get_text().strip().replace(
                            ',', '').replace(
                            '\n', ''))
                else:
                    collaboration.append(s.get_text().strip())
    except BaseException:
        pass
    course_level = t.select_one('div.level').get_text().strip()
    summary = t.select_one('div.card__expander--summary').get_text().strip()
    card_label = ''
    try:
        card_label = t.select_one('span.card').get_text().strip()
    except BaseException:
        pass
    datadict['href'] = href
    datadict['school'] = school
    datadict['title'] = title
    datadict['skills'] = skills
    datadict['collaboration'] = collaboration
    datadict['course_level'] = course_level
    datadict['summary'] = summary
    datadict['card_label'] = card_label
    outfile1.write(json.dumps(datadict, ensure_ascii=False) + '\n')
    outfile2.write(
        '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %
        (title,
         card_label,
         summary,
         course_level,
         ','.join(skills),
         school,
         ','.join(collaboration),
         href))
