import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('collector',Path(__file__).resolve().parents[1]/'scripts/collect.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class CollectorTests(unittest.TestCase):
    def row(self):return {'pblancId':'PBLN_123','pblancNm':'예비창업 사업화 모집','pblancUrl':'/web/lay1/bbs/view.do?pblancId=PBLN_123','reqstBeginEndDe':'20261201 ~ 20261231','trgetNm':'예비창업자','pldirSportRealmLclasCodeNm':'창업','bsnsSumryCn':'<p>지원 내용</p>'}
    def test_official_schema_and_aliases(self):
        result=c.unpack({'jsonArray':{'item':[self.row()]}})[0]
        self.assertEqual(result['deadline'],'2026-12-31');self.assertEqual(result['eligibility'],['예비창업자']);self.assertNotIn('<p>',result['description'])
        self.assertTrue(result['url'].startswith('https://www.bizinfo.go.kr/'))
        self.assertEqual(len(c.unpack({'jsonArray':[self.row(),self.row()]})),1)
    def test_ambiguous_dates(self):
        for value in ['예산 소진시까지','상시 접수','20261231','20260230 ~ 20261231']:
            self.assertEqual(c.dates(value),('',''))
    def test_error_and_truncation_do_not_become_empty_feed(self):
        with self.assertRaises(ValueError):c.unpack({'error':'bad key'})
        row=self.row();row['totCnt']='200'
        with self.assertRaises(ValueError):c.unpack({'jsonArray':[row]})
    def test_external_url_rejected(self):
        row=self.row();row['pblancUrl']='javascript:alert(1)'
        with self.assertRaises(ValueError):c.normalize(row)
if __name__=='__main__':unittest.main()
