#!/bin/bash

python manage.py dumpdata --indent=2 auth.User core.datatype core.unit core.organization core.grouping core.field core.eventtype core.datasheet core.datasheetfield core.project core.projectorganization core.media core.projectdatasheet core.state core.county core.site core.usertransaction > core/fixtures/dump_data.json
python manage.py dumpdata --indent=2 auth.User core > core/fixtures/dump_data_w_events.json
