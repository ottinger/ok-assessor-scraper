import unittest
from old import real_property
import datetime

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
        self.assertEqual(self.qsm.land_size, 1226214) # 28.15 * 43560
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
        self.assertEqual(bldg_1.remodel_year, 1999)
        self.assertEqual(bldg_1.building_name, "QUAIL SPRINGS MALL")
        self.assertEqual(bldg_1.alt_land_use_desc, "Commercial")
        self.assertEqual(bldg_1.quality_description, "Good")
        self.assertEqual(bldg_1.frame_description, "Masonry")
        self.assertEqual(bldg_1.foundation_description, "Slab")
        self.assertEqual(bldg_1.exterior, "")
        self.assertEqual(bldg_1.roof_type, "Flat")
        self.assertEqual(bldg_1.roof_cover, "Built Up Rock")
        self.assertEqual(bldg_1.avg_floor_height, 15)
        self.assertEqual(bldg_1.percent_sprinkled, 93)
        self.assertEqual(bldg_1.total_rooms, -1)
        self.assertEqual(bldg_1.bedrooms, -1)
        self.assertEqual(bldg_1.full_bathrooms, 0)
        self.assertEqual(bldg_1.three_quarters_bathrooms, 0)
        self.assertEqual(bldg_1.half_bathrooms, 0)
        self.assertEqual(bldg_1.hvac_type, "Package Unit")
        self.assertEqual(bldg_1.physical_condition, "Average")
        self.assertEqual(bldg_1.number_res_units, 0)
        self.assertEqual(bldg_1.number_comm_units, 125)

        bldg_2 = list(filter(lambda bldg: bldg.bldg_id==2, self.bldgs))[0]
        self.assertEqual(bldg_2.bldg_id, 2)
        self.assertEqual(bldg_2.vacant_or_improved, "Improved")
        self.assertEqual(bldg_2.bldg_description, "Theatre - Motion")
        self.assertEqual(bldg_2.year_built, 1998)
        self.assertEqual(bldg_2.sq_ft, 96340)
        self.assertEqual(bldg_2.number_stories, 1)
        self.assertEqual(bldg_2.remodel_year, -1)
        self.assertEqual(bldg_2.building_name, "QUAIL SPRINGS MALL")
        self.assertEqual(bldg_2.alt_land_use_desc, "Commercial")
        self.assertEqual(bldg_2.quality_description, "Very Good")
        self.assertEqual(bldg_2.frame_description, "Masonry")
        self.assertEqual(bldg_2.foundation_description, "Slab")
        self.assertEqual(bldg_2.exterior, "")
        self.assertEqual(bldg_2.roof_type, "Flat")
        self.assertEqual(bldg_2.roof_cover, "Built Up Rock")
        self.assertEqual(bldg_2.avg_floor_height, 35)
        self.assertEqual(bldg_2.percent_sprinkled, 100)
        self.assertEqual(bldg_2.total_rooms, -1)
        self.assertEqual(bldg_2.bedrooms, -1)
        self.assertEqual(bldg_2.full_bathrooms, 0)
        self.assertEqual(bldg_2.three_quarters_bathrooms, 0)
        self.assertEqual(bldg_2.half_bathrooms, 0)
        self.assertEqual(bldg_2.hvac_type, "Package Unit")
        self.assertEqual(bldg_2.physical_condition, "Good")
        self.assertEqual(bldg_2.number_res_units, 0)
        self.assertEqual(bldg_2.number_comm_units, 1)


# Test real property details for single-family home at 22466 Graces Ter (id=286936)
class GracesTest(unittest.TestCase):
    def setUp(self):
        self.graces = real_property.RealProperty(propertyid=286936)
        self.graces.extractRealPropertyData(propertyid=286936)
        self.graces.extractValuationHistory(286936)
        self.vals = self.graces.valuations
        self.graces.extractBuildings(286936)
        self.bldgs = self.graces.buildings
        self.graces.extractDeedHistory(286936)
        self.deedtransactions = self.graces.deedtransactions
        self.graces.extractBuildingPermits(286936)
        self.permits = self.graces.buildingpermits

    # Test fields in real_property.RealProperty
    def test_rp(self):
        self.assertEqual(self.graces.account_number,"R201761220")
        self.assertEqual(self.graces.property_type, "Residential")
        self.assertEqual(self.graces.location, "22466 GRACES TER")
        self.assertEqual(self.graces.building_name_occupant, "")
        self.assertEqual(self.graces.city, "UNINCORPORATED")
        # This test does not include owner name/address
        self.assertEqual(self.graces.quarter_section, 4631)
        # This test does not include owner name/address
        self.assertEqual(self.graces.parent_acct, "4631-25-908-8020")
        # This test does not include owner name/address
        self.assertEqual(self.graces.tax_district, "TXD 106FD2")
        # This test does not include owner name/address
        self.assertEqual(self.graces.school_system, "Deer Creek #6")
        # This test does not include owner name/address
        self.assertEqual(self.graces.land_size_str, "0.76 Acres")
        self.assertEqual(self.graces.land_size, 33105.6)
        self.assertEqual(self.graces.land_value, 65637)
        self.assertEqual(self.graces.quarter_section_description, "Sect 8-T14N-R3W Qtr SW")
        self.assertEqual(self.graces.subdivision, "SOUTHERLY FARMS SEC II")
        self.assertEqual(self.graces.block, "005")
        self.assertEqual(self.graces.lot, "037")

    # Test valuations
    def test_valuations(self):
        val_2018 = list(filter(lambda val: val.year==2018, self.vals))[0]
        self.assertEqual(val_2018.year, 2018)
        self.assertEqual(val_2018.market_value, 309500)
        self.assertEqual(val_2018.taxable_market_value, 298526)
        self.assertEqual(val_2018.gross_assessed, 32838)
        self.assertEqual(val_2018.exemption, 1000)
        self.assertEqual(val_2018.net_assessed, 31838)
        self.assertEqual(val_2018.millage, 118.05)
        self.assertEqual(val_2018.tax, 3758.46)
        self.assertEqual(val_2018.tax_savings, 260.55)

        # For 2006, market value and taxable market value are different, and county assessor
        # has no data for millage/tax/tax savings
        val_2006 = list(filter(lambda val: val.year==2006, self.vals))[0]
        self.assertEqual(val_2006.year, 2006)
        self.assertEqual(val_2006.market_value, 263306)
        self.assertEqual(val_2006.taxable_market_value, 256182)
        self.assertEqual(val_2006.gross_assessed, 28179)
        self.assertEqual(val_2006.exemption, 1000)
        self.assertEqual(val_2006.net_assessed, 27179)
        self.assertEqual(val_2006.millage, 0)
        self.assertEqual(val_2006.tax, 0)
        self.assertEqual(val_2006.tax_savings, 0)

    # Test building info table
    def test_buildings(self):
        self.assertEqual(len(self.bldgs), 1)

        bldg_1 = list(filter(lambda bldg: bldg.bldg_id==1, self.bldgs))[0]
        self.assertEqual(bldg_1.bldg_id, 1)
        self.assertEqual(bldg_1.vacant_or_improved, "Improved")
        self.assertEqual(bldg_1.bldg_description, "Ranch 1 Story")
        self.assertEqual(bldg_1.year_built, 2001)
        self.assertEqual(bldg_1.sq_ft, 2694)
        self.assertEqual(bldg_1.number_stories, 1)
        self.assertEqual(bldg_1.remodel_year, -1)
        self.assertEqual(bldg_1.building_name, "")
        self.assertEqual(bldg_1.alt_land_use_desc, "Residential Improvement")
        self.assertEqual(bldg_1.quality_description, "Good")
        self.assertEqual(bldg_1.frame_description, "")
        self.assertEqual(bldg_1.foundation_description, "Slab")
        self.assertEqual(bldg_1.exterior, "Frame Masonry Veneer")
        self.assertEqual(bldg_1.roof_type, "Hip/Gable")
        self.assertEqual(bldg_1.roof_cover, "Composition Shingle")
        self.assertEqual(bldg_1.avg_floor_height, 8)
        self.assertEqual(bldg_1.percent_sprinkled, 0)
        self.assertEqual(bldg_1.total_rooms, 7)
        self.assertEqual(bldg_1.bedrooms, 3)
        self.assertEqual(bldg_1.full_bathrooms, 3)
        self.assertEqual(bldg_1.three_quarters_bathrooms, 0)
        self.assertEqual(bldg_1.half_bathrooms, 0)
        self.assertEqual(bldg_1.hvac_type, "Central Air to Air")
        self.assertEqual(bldg_1.physical_condition, "Average")
        self.assertEqual(bldg_1.number_res_units, 1)
        self.assertEqual(bldg_1.number_comm_units, 0)

    def test_deedtransactions(self):
        self.assertGreaterEqual(len(self.deedtransactions), 7)

        tx_list = list(filter(lambda tx: tx.date.date() == datetime.date(2001, 1, 2), self.deedtransactions))
        self.assertEqual(len(tx_list), 1)
        first_tx = tx_list[0]

        self.assertEqual(first_tx.type, "Deeds")
        self.assertEqual(first_tx.book, 7990)
        self.assertEqual(first_tx.page, 1571)
        self.assertEqual(first_tx.price, 30000)
        self.assertEqual(first_tx.grantor, "SOUTHERLY FARMS LLC")
        self.assertEqual(first_tx.grantee, "FREEMAN HOMES INC")

    # Test building permits
    def test_permits(self):
        self.assertGreaterEqual(len(self.permits), 1)

        tp = list(filter(lambda tx: tx.date.date() == datetime.date(2001, 1, 10), self.permits))
        self.assertEqual(len(tp), 1)
        test_permit = tp[0]

        self.assertEqual(test_permit.permit_number, "10271800")
        self.assertEqual(test_permit.provided_by, "COUNTY")
        self.assertEqual(test_permit.building_number, 1)
        self.assertEqual(test_permit.description, "Main Dwellin") # Yes, there's no "g"
        self.assertEqual(test_permit.estimated_cost, 180000)
        self.assertEqual(test_permit.status, "Inactive")