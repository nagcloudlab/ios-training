"""Unit 04 settings, exec'd by each Unit 04 generator after gen02's helpers (S defined):
    exec(open(os.path.join(HERE, 'unit4.py')).read())
Reuses Unit 02's evidence helpers (mono, tbl, console, shot, PHONE, crop, SIM). Lesson names come from the Lesson 4.1
text's Unit 4 learning sequence (section 9)."""
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 01/02 helpers
UNIT_NO, UNIT_TITLE = '04', 'Application Architecture &amp; MVVM'
UNIT_LESSONS = [('4.1', 'Architecture', ''), ('4.2', 'MVVM', ''), ('4.3', 'Observation', ''), ('4.4', 'Dependency', 'injection'),
                ('4.5', 'Repository', ''), ('4.6', 'Use cases', ''), ('4.7', 'UI state', ''), ('4.8', 'Modules', ''),
                ('4.9', 'Testing', ''), ('4.10', 'Integration', 'lab')]
