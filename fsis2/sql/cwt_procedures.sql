--select * from foofunc('4-4');

-- this script contains the sql code to create stored procedured used by fsis-II to 
-- to return cwt stoced and recoved in a particular region of interest.
-- regions can identifed by the management unit slug or a geometry object
-- each function includes agruments to control the first and last years to include 
-- as well as the species or strain id to include.

-- stored procedures in this script are intended to be used with django raw sql manager.  
-- each of the functions return recordset set of either cwt_recoveries or stocking events

--    + cwt_stocking_events_geom(geom, fyear, lyear, spc_ids)
--    + cwt_stocking_events_mu(geom, fyear, lyear, spc_ids)
--    + cwt_recovered_geom(geom, fyear, lyear, spc_ids)
--    + cwt_recovered_mu(geom, fyear, lyear, spc_ids)
--
--    + seq_cwt_stocked_geom(geom, fyear, lyear, spc_ids)
--    + seq_cwt_stocked_mu(geom, fyear, lyear, spc_ids)
--    + seq_cwt_recovered_geom(geom, fyear, lyear, spc_ids)
--    + seq_cwt_recovered_mu(geom, fyear, lyear, spc_ids)
--
--    + what about strains?? One option might be:
--    + seq_cwt_stocked_geom(geom, fyear, lyear, strain_ids)
--      the forms used here would return the strains_id and which would
--      be presented on the form by species:



CREATE OR REPLACE FUNCTION cwts_recovered_geom(_geom geometry, 
						_fyear int, 
						_lyear int, 
						_spc_ids int[] DEFAULT '{}') 

-- given a polygon, return all of the recoveries of cwts stocked in the geom between 
--the first and last year.  If no species ids are provided, all species are returned.

RETURNS SETOF cwts_cwt_recovery AS 
$func$
BEGIN
IF _spc_ids <> '{}'::int[] then
RETURN QUERY

SELECT distinct cwt_recovery.* 
FROM cwts_cwt_recovery AS cwt_recovery
JOIN fsis2_species AS spc on spc.id=cwt_recovery.spc_id
  JOIN (SELECT DISTINCT fs_event.id,
               cwt,
               species_id
        FROM fsis2_cwts_applied AS cwts_applied
          JOIN fsis2_taggingevent AS tagging_event ON cwts_applied.tagging_event_id = tagging_event.id
          JOIN fsis2_event AS fs_event ON fs_event.id = tagging_event.stocking_event_id
          JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
          JOIN fsis2_species AS spc on spc.id=lot.species_id
        WHERE 
        fs_event.year >= _fyear and
        fs_event.year <= _lyear and
        tagging_event.tag_type=6 and -- normal cwts        
        spc.id = ANY(_spc_ids) and
        st_intersects (fs_event.geom,_geom)) AS events
    ON (events.species_id = cwt_recovery.spc_id
   AND events.cwt = cwt_recovery.cwt);

ELSE
RETURN QUERY

SELECT distinct cwt_recovery.* 
FROM cwts_cwt_recovery AS cwt_recovery
JOIN fsis2_species AS spc on spc.id=cwt_recovery.spc_id
  JOIN (SELECT DISTINCT fs_event.id,
               cwt,
               species_id
        FROM fsis2_cwts_applied AS cwts_applied
          JOIN fsis2_taggingevent AS tagging_event ON cwts_applied.tagging_event_id=tagging_event.id
          JOIN fsis2_event AS fs_event ON fs_event.id=tagging_event.stocking_event_id
          JOIN fsis2_lot AS lot ON lot.id=fs_event.lot_id
          JOIN fsis2_species AS spc ON spc.id=lot.species_id
        WHERE 
        fs_event.year >= _fyear AND
        fs_event.year <= _lyear AND       
        tagging_event.tag_type=6 AND
        st_intersects (fs_event.geom,_geom)) AS events
    ON (events.species_id = cwt_recovery.spc_id
   AND events.cwt = cwt_recovery.cwt);

END IF;
END;
$func$  LANGUAGE 'plpgsql'

-- without speceis ids:
select * from cwts_recovered_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1995, 2001);

-- with several speceis ids:
select * from cwts_recovered_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1990, 2005,  VARIADIC ARRAY[31, 35, 39]);

-- with one species id
select * from cwts_recovered_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1990, 2005,  VARIADIC ARRAY[39]);



CREATE OR REPLACE FUNCTION cwts_recovered_mu(_mu_slug char, 
						_fyear int, 
						_lyear int, 
						_spc_ids int[] DEFAULT '{}') 

-- given slug for a management unit, return all of the recoveries of cwts stocked in the management unit between 
--the first and last year.  If no species ids are provided, all species are returned.

RETURNS SETOF cwts_cwt_recovery AS 
$func$
BEGIN
IF _spc_ids <> '{}'::int[] then
RETURN QUERY

SELECT distinct cwt_recovery.* 
FROM cwts_cwt_recovery AS cwt_recovery
JOIN fsis2_species AS spc on spc.id=cwt_recovery.spc_id
  JOIN (SELECT DISTINCT fs_event.id,
               cwt,
               species_id
        FROM fsis2_cwts_applied AS cwts_applied
          JOIN fsis2_taggingevent AS tagging_event ON cwts_applied.tagging_event_id = tagging_event.id
          JOIN fsis2_event AS fs_event ON fs_event.id = tagging_event.stocking_event_id
          JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
          JOIN fsis2_species AS spc on spc.id=lot.species_id
        WHERE 
        fs_event.year >= _fyear and
        fs_event.year <= _lyear and
        tagging_event.tag_type=6 and -- normal cwts        
        spc.id = ANY(_spc_ids) and
        st_intersects (fs_event.geom,(select geom from fsis2_managementunit where slug=_mu_slug))) AS events
    ON (events.species_id = cwt_recovery.spc_id
   AND events.cwt = cwt_recovery.cwt);

ELSE
RETURN QUERY

SELECT distinct cwt_recovery.* 
FROM cwts_cwt_recovery AS cwt_recovery
JOIN fsis2_species AS spc on spc.id=cwt_recovery.spc_id
  JOIN (SELECT DISTINCT fs_event.id,
               cwt,
               species_id
        FROM fsis2_cwts_applied AS cwts_applied
          JOIN fsis2_taggingevent AS tagging_event ON cwts_applied.tagging_event_id=tagging_event.id
          JOIN fsis2_event AS fs_event ON fs_event.id=tagging_event.stocking_event_id
          JOIN fsis2_lot AS lot ON lot.id=fs_event.lot_id
          JOIN fsis2_species AS spc ON spc.id=lot.species_id
        WHERE 
        fs_event.year >= _fyear AND
        fs_event.year <= _lyear AND       
        tagging_event.tag_type=6 AND
        st_intersects (fs_event.geom, (select geom from fsis2_managementunit where slug=_mu_slug))) AS events
    ON (events.species_id = cwt_recovery.spc_id
   AND events.cwt = cwt_recovery.cwt);

END IF;
END;
$func$  LANGUAGE 'plpgsql'

-- without speceis ids:
select * from cwts_recovered_mu('5-8', 1995, 2001) limit 20;

-- with several speceis ids:
select * from cwts_recovered_mu('6-1', 1990, 2005,  VARIADIC ARRAY[31, 35, 39]);

-- with one species id
select * from cwts_recovered_mu('4-4', 1990, 2005,  VARIADIC ARRAY[39]) limit 20;



--====================================================================
CREATE OR REPLACE FUNCTION cwts_stocking_events_mu(_mu_slug char, 
						   _fyear int, 
						   _lyear int, 
						   _spc_ids int[] DEFAULT '{}') 

-- given slug for a management unit, return all of the stocking event associated with cwts recovered 
-- in the management unit between the first and last year.  If no species ids are provided, 
-- all species are returned.

RETURNS SETOF fsis2_event AS 
$func$
BEGIN
IF _spc_ids <> '{}'::int[] then
RETURN QUERY


SELECT distinct fs_event.*
FROM fsis2_event AS fs_event
  JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
  JOIN fsis2_species as spc on spc.id=lot.species_id
  JOIN fsis2_taggingevent AS tagging_event ON tagging_event.stocking_event_id = fs_event.id
  JOIN fsis2_cwts_applied cwts_applied ON cwts_applied.tagging_event_id = tagging_event.id
  JOIN (SELECT cwt,
               spc_id
        FROM cwts_cwt_recovery AS recovery
        JOIN fsis2_species spc on spc.id=recovery.spc_id
        WHERE 
        spc.id = ANY(_spc_ids) and 
        recovery.recovery_year >= _fyear and 
        recovery.recovery_year <= _lyear and
        st_intersects (recovery.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = _mu_slug))) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)
   WHERE tagging_event.tag_type=6;


ELSE
RETURN QUERY

SELECT distinct fs_event.*
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
        recovery.recovery_year >= _fyear and 
        recovery.recovery_year <= _lyear and
        st_intersects (recovery.geom,(SELECT geom FROM fsis2_managementunit WHERE slug = _mu_slug))) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)
   WHERE tagging_event.tag_type=6;

END IF;
END;
$func$  LANGUAGE 'plpgsql'

-- without speceis ids:
select * from cwts_stocking_events_mu('5-8', 1995, 2001) limit 20;

-- with several speceis ids:
select * from cwts_stocking_events_mu('6-1', 1990, 2005,  VARIADIC ARRAY[31, 35, 39]);

-- with one species id
select * from cwts_stocking_events_mu('4-4', 1990, 2005,  VARIADIC ARRAY[39]) limit 20;


--===============================================================

CREATE OR REPLACE FUNCTION cwts_stocking_events_geom(_geom geometry, 
						   _fyear int, 
						   _lyear int, 
						   _spc_ids int[] DEFAULT '{}') 

-- given geometry for a region of interest, return all of the stocking event associated with cwts recovered 
-- in the region of interest between the first and last year.  If no species ids are provided, 
-- all species are returned.

RETURNS SETOF fsis2_event AS 
$func$
BEGIN
IF _spc_ids <> '{}'::int[] then
RETURN QUERY


SELECT distinct fs_event.*
FROM fsis2_event AS fs_event
  JOIN fsis2_lot AS lot ON lot.id = fs_event.lot_id
  JOIN fsis2_species as spc on spc.id=lot.species_id
  JOIN fsis2_taggingevent AS tagging_event ON tagging_event.stocking_event_id = fs_event.id
  JOIN fsis2_cwts_applied cwts_applied ON cwts_applied.tagging_event_id = tagging_event.id
  JOIN (SELECT cwt,
               spc_id
        FROM cwts_cwt_recovery AS recovery
        JOIN fsis2_species spc on spc.id=recovery.spc_id
        WHERE 
        spc.id = ANY(_spc_ids) and 
        recovery.recovery_year >= _fyear and 
        recovery.recovery_year <= _lyear and
        st_intersects (recovery.geom,_geom)) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)
   WHERE tagging_event.tag_type=6;


ELSE
RETURN QUERY

SELECT distinct fs_event.*
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
        recovery.recovery_year >= _fyear and 
        recovery.recovery_year <= _lyear and
        st_intersects (recovery.geom,_geom)) AS cwts
    ON (cwts.cwt = cwts_applied.cwt
   AND cwts.spc_id = lot.species_id)
   WHERE tagging_event.tag_type=6;

END IF;
END;
$func$  LANGUAGE 'plpgsql'

-- without speceis ids:
select * from cwts_stocking_events_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1995, 2001);

-- with several speceis ids:
select * from cwts_stocking_events_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1990, 2005,  VARIADIC ARRAY[31, 35, 39]);

-- with one species id
select * from cwts_stocking_events_geom(
	st_setsrid(st_geomfromgeojson(
		'{"type": "Polygon", "coordinates": [[
		[-82.271, 45.514], 
		[-82.380, 44.512], 
		[-81.128, 44.449], 
		[-81.172, 45.406], 
		[-82.271, 45.514]]]}'),4326), 1990, 2005,  VARIADIC ARRAY[39]);




