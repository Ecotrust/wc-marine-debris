-- Create a "view" for searching debris collection data from Marine Planner
-- PG 9.1 doesn't support materialized views, so this is a regular table that
-- will have to be regenerated periodically. 
-- SRH 15-Aug-2014

drop table if exists event_ontology;

create table event_ontology as 
select 
e.id as event_id,
e.cleanupdate,
s.sitename,
t.type,
ST_AsGeoJSON(s.geometry, 15, 0) as geometry,
f.internal_name,
f.label,
f.id field_id,
fu.short_name unit,
fv.field_value,
case when field_value ~ '^[0-9]+(\.[0-9]+)?$' then
    cast(field_value as float)
else
    NULL
end as field_value_float,
fv.id field_value_id,
ds.id datasheet_id,
dt.name datatype,
dt.aggregatable,
ds.slug datasheet,
p.slug project,
o.slug organization

from 

core_fieldvalue fv 
join core_field f on fv.field_id_id = f.id
    join core_datatype dt on dt.id = f.datatype_id
    join core_unit fu on fu.id = f.unit_id_id
join core_event e on fv.event_id_id = e.id
    join core_site s on e.site_id = s.id -- 442078
join core_usertransaction ut on e.transaction_id = ut.id and ut.status = 'accepted'  -- 439824

    join core_project p on ut.project_id = p.id -- 203731; about half the data was uploaded prior to the usertransaction foreign keys to project and organization, so that data isn't associated with anything (except maybe the user)
        join core_projectdatasheet pds on p.id = pds.project_id_id
        join core_datasheet ds on ds.id = pds.sheet_id_id
        join core_eventtype t on ds.type_id_id = t.id

join core_organization o on ut.organization_id = o.id

where 
field_value <> 'None'
and field_value <> ''
;

alter table event_ontology add column id bigserial primary key;
create index field_internal_name_idx on event_ontology (internal_name);
-- create index field_value_idx on event_ontology (field_value);
-- create index field_data on event_ontology(internal_name, field_value);

-- select count(*) from event_ontology;
