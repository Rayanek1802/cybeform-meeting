#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from services.report_generator import ReportGenerator

gen = ReportGenerator()
test_str = "{'decision': 'Valider les calculs avec le bureau d\\'études spécialisé', 'context': 'Sécurisation des équipements', 'contexteTemporel': '[16:08-24:15]'}"
print(f'Input: {test_str}')
result = gen._parse_dict_string(test_str)
print(f'Result: {result}')
for k, v in result.items():
    print(f'  {k}: {repr(v)}')