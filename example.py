#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bottle
from bottle.ext import beakersession
import os

bottle.install(beakersession.Plugin(config={
        'auto': True,
        'cookie_expires': True,
        'type': 'memory',
        'key': 'example_sid',
}))

template_links = '''
<br>
<a href="/">reload</a>
<a href="/show">show session data</a>
<a href="/delete">delete session</a>
'''

template_index = '''
Hello {{ name }}<br>
Test counter {{ counter }}<br>
''' + template_links

template_name = '''
<form method="POST">
    <label for="name">Please enter your name</label>
    <input type="text" name="name" id="name">
    <input type="submit">
</form>
''' + template_links

template_show = '''
<table>
%for key, value in session:
    <tr><td>{{key}}</td><td>{{value}}</td></tr>
%end
</table>
''' + template_links

@bottle.get('/')
def index(session):
    if 'name' not in session:
        bottle.redirect('/enter_name')
    session['counter'] = session.get('counter', 0) + 1
    return bottle.template(template_index, {'name':session['name'], 'counter':session['counter']})

@bottle.get('/enter_name', method=['GET', 'POST'])
def enter_name(session):
    name = bottle.request.forms.get('name', '').strip()
    if len(name) > 0:
        session['name'] = name
        bottle.redirect('/')
    return bottle.template(template_name)

@bottle.get('/delete')
def delete(session):
    session.delete()
    bottle.redirect('/')

@bottle.get('/show')
def show(session):
    return bottle.template(template_show, {'session':session.items()})

bottle.debug(True)
bottle.run(reloader=True)
