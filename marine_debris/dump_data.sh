#!/bin/bash

python manage.py dumpdata --indent=2 auth.User flatblocks.flatblock core.datatype core.unit core.unitconversion core.download core.organization core.grouping core.answeroption core.displaycategory core.field core.eventtype core.datasheet core.datasheetfield core.project core.projectorganization core.media core.projectdatasheet core.state core.usertransaction core.site core.county > core/fixtures/dump_data.json
python manage.py dumpdata --indent=2 flatblocks.flatblock core.datatype core.unit core.unitconversion core.download core.organization core.grouping core.answeroption core.displaycategory core.field core.eventtype core.datasheet core.datasheetfield core.project core.projectorganization core.media core.projectdatasheet core.state core.site core.usertransaction core.county > core/fixtures/update_data.json
python manage.py dumpdata --indent=2 auth.User flatblocks.flatblock core > core/fixtures/dump_data_w_events.json
