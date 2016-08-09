--['manage.py', 'sqlclear', 'fsis2', '--settings=main.settings.local']
BEGIN;
DROP TABLE "fsis2_managementunit";
DROP TABLE "fsis2_lake";
DROP TABLE "fsis2_cwts_applied";
DROP TABLE "fsis2_taggingevent";
DROP TABLE "fsis2_event";
DROP TABLE "fsis2_lot";
DROP TABLE "fsis2_stockingsite";
DROP TABLE "fsis2_proponent";
DROP TABLE "fsis2_strain";
DROP TABLE "fsis2_species";
DROP TABLE "fsis2_readme";
DROP TABLE "fsis2_builddate";

COMMIT;
