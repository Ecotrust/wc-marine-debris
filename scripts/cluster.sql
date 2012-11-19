\pset pager
select count(*), round(cast (ST_X(geometry) as numeric),3), round(cast (ST_Y(geometry) as numeric),3)
from core_site group by round(cast (ST_X(geometry) as numeric),3), round(cast (ST_Y(geometry) as numeric),3);
