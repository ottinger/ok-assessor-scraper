import unittest
import real_property
import rp_tables

# Test real property details for Quail Springs Mall, 2501 W Memorial Rd (id=223240)
class QuailSpringsTest(unittest.TestCase):
    def setUp(self):
        self.qsm = real_property.RealProperty(propertyid=223240)
        self.qsm.extractRealPropertyData(propertyid=223240)
        self.qsm.extractValuationHistory(223240)
        self.vals = self.qsm.valuations
        self.qsm.extractBuildings(223240)
        self.bldgs = self.qsm.buildings

    # Test fields in real_property.RealProperty
    def test_rp(self):
        self.assertEqual(self.qsm.account_number,"R110111000")
        self.assertEqual(self.qsm.property_type, "Commercial")
        self.assertEqual(self.qsm.location, "2501 W MEMORIAL RD")
        self.assertEqual(self.qsm.building_name_occupant, "QUAIL SPRINGS MALL")
        self.assertEqual(self.qsm.city, "OKLAHOMA CITY")
        self.assertEqual(self.qsm.owner_name_1, "QUAIL SPRINGS MALL LLC")
        self.assertEqual(self.qsm.quarter_section, 3626)
        self.assertEqual(self.qsm.owner_name_2, "")
        self.assertEqual(self.qsm.parent_acct, "")
        self.assertEqual(self.qsm.billing_address_1, "C/O GENERAL GROWTH PROP BSC 3 04")
        self.assertEqual(self.qsm.tax_district, "TXD 212")
        self.assertEqual(self.qsm.billing_address_2, "PO BOX 617905")
        self.assertEqual(self.qsm.school_system, "Edmond #12")
        self.assertEqual(self.qsm.city_state_zip, "CHICAGO, IL 60661-7905")
        self.assertEqual(self.qsm.land_size_str, "28.15 Acres")
        self.assertEqual(self.qsm.land_value, 3358838)
        self.assertEqual(self.qsm.quarter_section_description, "Sect 7-T13N-R3W Qtr SE")
        self.assertEqual(self.qsm.subdivision, "QUAIL SPRINGS MALL")
        self.assertEqual(self.qsm.block, "001")
        self.assertEqual(self.qsm.lot, "000")

    # Test valuations
    def test_valuations(self):
        val_2018 = list(filter(lambda val: val.year==2018, self.vals))[0]
        self.assertEqual(val_2018.year, 2018)
        self.assertEqual(val_2018.market_value, 61581618)
        self.assertEqual(val_2018.taxable_market_value, 61581618)
        self.assertEqual(val_2018.gross_assessed, 6773978)
        self.assertEqual(val_2018.exemption, 0)
        self.assertEqual(val_2018.net_assessed, 6773978)
        self.assertEqual(val_2018.millage, 122.06)
        self.assertEqual(val_2018.tax, 826831.75)
        self.assertEqual(val_2018.tax_savings, 0.0)

        # For 2006, market value and taxable market value are different, and county assessor
        # has no data for millage/tax/tax savings
        val_2006 = list(filter(lambda val: val.year==2006, self.vals))[0]
        self.assertEqual(val_2006.year, 2006)
        self.assertEqual(val_2006.market_value, 71527665)
        self.assertEqual(val_2006.taxable_market_value, 71370036)
        self.assertEqual(val_2006.gross_assessed, 7850702)
        self.assertEqual(val_2006.exemption, 0)
        self.assertEqual(val_2006.net_assessed, 7850702)
        self.assertEqual(val_2006.millage, 0)
        self.assertEqual(val_2006.tax, 0)
        self.assertEqual(val_2006.tax_savings, 0)

    # Test building info table
    def test_buildings(self):
        self.assertEqual(len(self.bldgs), 2)

        bldg_1 = list(filter(lambda bldg: bldg.bldg_id==1, self.bldgs))[0]
        self.assertEqual(bldg_1.bldg_id, 1)
        self.assertEqual(bldg_1.vacant_or_improved, "Improved")
        self.assertEqual(bldg_1.bldg_description, "Regional Shopping Center")
        self.assertEqual(bldg_1.year_built, 1980)
        self.assertEqual(bldg_1.sq_ft, 497994)
        self.assertEqual(bldg_1.number_stories, 3)

        bldg_2 = list(filter(lambda bldg: bldg.bldg_id==2, self.bldgs))[0]
        self.assertEqual(bldg_2.bldg_id, 2)
        self.assertEqual(bldg_2.vacant_or_improved, "Improved")
        self.assertEqual(bldg_2.bldg_description, "Theatre - Motion")
        self.assertEqual(bldg_2.year_built, 1998)
        self.assertEqual(bldg_2.sq_ft, 96340)
        self.assertEqual(bldg_2.number_stories, 1)