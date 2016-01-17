--- this sql script is my first attempt at create sql code that will return all of 
-- the cwt recoveries and stocking events from a region of interest.  In all cases, 
-- species is used in the join to match stocking events and recoveries


select geom from fsis2_managementunit where slug='ltrz-12';
-- recovery objects in ltrz-12
SELECT *
FROM cwts_cwt_recovery AS recovery
WHERE st_intersects (recovery.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = 'ltrz-12'));

-- now get the associated stocking events for those cwts:
select * from cwts_cwt_recovery limit 10;
select * from fsis2_lot limit 10;
select * from fsis2_event limit 10;
select * from fsis2_taggingevent limit 10;
select * from fsis2_cwts_applied limit 10;

-- this query returns OMNR stocking events associated with cwts recovered in a ltrz
-- only events with the same species and the recoverev cwt is returned.
SELECT distinct spc.common_name, fs_event.*
FROM fsis2_event AS fs_event
  JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
  join fsis2_species as spc on spc.id=lot.species_id
  JOIN fsis2_taggingevent AS tagging_event ON tagging_event.stocking_event_id = fs_event.id
  JOIN fsis2_cwts_applied cwts_applied ON cwts_applied.tagging_event_id = tagging_event.id
  JOIN (SELECT cwt,
               spc_id
        FROM cwts_cwt_recovery AS recovery
        WHERE st_intersects (recovery.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = 'ltrz-12'))) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)


-- same as above but with a filter on species code and recovery year:
SELECT distinct spc.common_name, fs_event.*
FROM fsis2_event AS fs_event
  JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
  join fsis2_species as spc on spc.id=lot.species_id
  JOIN fsis2_taggingevent AS tagging_event ON tagging_event.stocking_event_id = fs_event.id
  JOIN fsis2_cwts_applied cwts_applied ON cwts_applied.tagging_event_id = tagging_event.id
  JOIN (SELECT cwt,
               spc_id
        FROM cwts_cwt_recovery AS recovery
        join fsis2_species spc on spc.id=recovery.spc_id
        WHERE 
        spc.species_code in (75,81) and 
        recovery.recovery_year>1992 and 
        recovery.recovery_year<1995 and
        st_intersects (recovery.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = 'ltrz-12'))) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)


-- now find all of the recoveries of stocking events in a roi given a species code, first year and last year:
SELECT distinct common_name, cwt_recovery.*
FROM cwts_cwt_recovery AS cwt_recovery
join fsis2_species as spc on spc.id=cwt_recovery.spc_id
  JOIN (SELECT DISTINCT fs_event.id,
               cwt,
               species_id
        FROM fsis2_cwts_applied AS cwts_applied
          JOIN fsis2_taggingevent AS tagging_event ON cwts_applied.tagging_event_id = tagging_event.id
          JOIN fsis2_event AS fs_event ON fs_event.id = tagging_event.stocking_event_id
          JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
          join fsis2_species as spc on spc.id=lot.species_id
        WHERE 
        fs_event.year >= 1900 and
        fs_event.year <= 2055 and
        spc.species_code in (81) and
        st_intersects (fs_event.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = '5-7'))) AS events
    ON (events.species_id = cwt_recovery.spc_id
   AND events.cwt = cwt_recovery.cwt);

select distinct slug from fsis2_managementunit;
select * from cwts_cwt_recovery as recovery where cwt !~ '\d{6}' limit 10;




--CREATE FUNCTION foofunc()
			--_fear int DEFAULT 1950,
			--_lyear int DEFAULT 2050,
			--_spc_ids int [] DEFAULT '{}'
			--) 
--CREATE FUNCTION foofunc() RETURNS SETOF cwts_cwt_recovery AS 'SELECT * FROM cwts_cwt_recovery
CREATE OR REPLACE FUNCTION foofunc (_fyear int DEFAULT 1950,
	                                  _lyear int DEFAULT 2100
	                                  ) RETURNS setof cwts_cwt_recovery
AS 
$$
select * from cwts_cwt_recovery as r
WHERE r.recovery_year >= _fyear
AND   r.recovery_year <= _lyear 

LIMIT 10;
$$
LANGUAGE 'plpgsql';


select * from foofunc();
select * from foofunc(2002, 2006);

drop function foofunc();

create function GetSpecies() returns setof fsis2_species as 'select * from fsis2_species;' language 'sql';
drop function GetSpecies();
select * from getspecies();
