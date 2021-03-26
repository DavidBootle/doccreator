from tools import *

teams = Path.load('teams.json')

teams.render('rendered.md')