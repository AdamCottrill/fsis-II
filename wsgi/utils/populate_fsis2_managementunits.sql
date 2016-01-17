-- this script can be used to insert the geometries in the ltrz and qma shapefiles into fsis2_managementunit

-- verify that twe have the tables we need:
select * from shapefiles.ltrz limit 2;
select * from shapefiles.qma limit 2;

select * from fsis2_managementunit;

-- see if we have any invalid geometries in the qma table:
SELECT on_manarea,
       geom
FROM shapefiles.qma
WHERE st_isvalid (geom) IS FALSE;

-- fix those ones that aren't valid:
--update shapefiles.qma set geom=st_buffer(geom,0.0000001) where st_isvalid(geom) is false;
-- alternatively:
ALTER TABLE shapefiles.qma ALTER COLUMN geom TYPE geometry ('MULTIPOLYGON',26917) USING st_collectionextract (st_makevalid (geom),3);
-- after the correction:
SELECT on_manarea,
       geom
FROM shapefiles.qma
WHERE st_isvalid (geom) IS FALSE;


-- now insert the geometries into fsis2_managent unit.  This will have to be more
-- involved if we ever add more tables, for now it's fine.

insert into fsis2_lake (lake) values ('Lake Huron');
-- addin our ltrzs first
insert into fsis2_managementunit
select gid as id, 'LTRZ-' || ltrz as label, 'ltrz-' || ltrz as slug, 
st_multi(st_transform(st_simplify(geom,10), 4326)) as geom,
1 as lake_id, 'ltrz' as mu_type  from shapefiles.ltrz ;

-- addin our qmas
insert into fsis2_managementunit
select row_number() over (ORDER BY st_union(geom)) + 18 as id, on_manarea as label, on_manarea as slug, 
st_multi(st_union(st_transform(geom, 4326))) as geom,
1 as lake_id, 'qma' as mu_type from shapefiles.qma 
group by on_manarea
having on_manarea is not null order by label;

commit;





