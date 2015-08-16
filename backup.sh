#!/bin/sh
pg_dump -U root -d mun > mun.psql.bak.`date +%Y.%m.%d`
