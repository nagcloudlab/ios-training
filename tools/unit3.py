"""Unit 03 settings, exec'd by each Unit 03 generator after gen02's helpers (S defined):
    exec(open(os.path.join(HERE, 'unit3.py')).read())
Reuses Unit 02's evidence helpers (mono, tbl, console, shot, PHONE, crop, SIM). Lessons are named from their texts
(the user's Unit 3 texts differ from the curriculum plan's 3.x titles)."""
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 01/02 helpers
UNIT_NO, UNIT_TITLE = '03', 'Advanced SwiftUI &amp; Navigation'
UNIT_LESSONS = [('3.1', 'Navigation', 'Stack'), ('3.2', 'Typed', 'routes'), ('3.3', 'TabView', ''), ('3.4', 'Sheets &amp;', 'alerts'),
                ('3.5', 'State', 'preservation'), ('3.6', 'Animations', ''), ('3.7', 'Design', 'system'), ('3.8', 'Adaptive', 'layouts'),
                ('3.9', 'Environment', ''), ('3.10', 'Accessibility', '&amp; l10n'), ('3.11', 'Performance', ''),
                ('3.12', 'Integration', 'review')]   # Unit 3 runs to twelve lessons (stated with the 3.10 text)
