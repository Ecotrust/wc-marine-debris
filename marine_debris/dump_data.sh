#!/bin/bash

python manage.py dumpdata --indent=2 auth.User core > core/fixtures/dump_data.json
