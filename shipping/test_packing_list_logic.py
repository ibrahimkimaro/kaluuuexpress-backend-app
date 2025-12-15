import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Mock django modules
import sys
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.utils'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

# Now we can define a dummy PackingList class that mimics the real one
class PackingList:
    objects = MagicMock()
    
    def __init__(self):
        self.code = None
        self.date = datetime.now().date()
    
    def save(self):
        if not self.code:
            # Logic from the actual model
            today = self.date
            date_str = today.strftime('%Y%m%d')
            
            # Get last packing list for today
            last_pl = PackingList.objects.filter(
                code__startswith=f'PL-{date_str}'
            ).order_by('-code').first()
            
            if last_pl:
                last_num = int(last_pl.code.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.code = f'PL-{date_str}-{new_num:03d}'

class TestPackingListLogic(unittest.TestCase):
    def test_generate_code_first_of_day(self):
        # Setup mock
        PackingList.objects.filter.return_value.order_by.return_value.first.return_value = None
        
        pl = PackingList()
        # Mock date to a fixed value
        fixed_date = datetime(2025, 12, 16)
        pl.date = fixed_date
        
        pl.save()
        
        expected_code = "PL-20251216-001"
        self.assertEqual(pl.code, expected_code)
        
    def test_generate_code_increment(self):
        # Setup mock to return an existing list
        last_pl = MagicMock()
        last_pl.code = "PL-20251216-005"
        
        PackingList.objects.filter.return_value.order_by.return_value.first.return_value = last_pl
        
        pl = PackingList()
        # Mock date to a fixed value
        fixed_date = datetime(2025, 12, 16)
        pl.date = fixed_date
        
        pl.save()
        
        expected_code = "PL-20251216-006"
        self.assertEqual(pl.code, expected_code)

if __name__ == '__main__':
    unittest.main()
