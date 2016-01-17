FSIS-II
=======

Background
----------

FSIS-II was build to graphically display fish stocking data for the
Ontario waters of Lake Huron.

Originally developed as an exercise in developing a web-based,
geo-enabled application, FSIS-II has proven to be an effective tool
for reporting and data review. This is particularly with respect to
the complicate relationships between stocking events, coded wire tags
and subsequent recoveries.


Data Model
----------

The underlying data model for FSIS-II is based on hierarchical
relationship between a lot of fish which can be stocked in one or more
stocking events.  A lot of fish is defined as a group of fish of the
same species, strain, and year class, raised by a single proponent
(hatchery).

Tags (both coded wire and standard) are modelled using a many-to-many
relationship to stocking events.  Sequential coded wire tags are a
special case of standard cwt.  If multiple cwts are returned, they are
rendered in the response along with an appropriate warning.

Additional tables are included in the data model to accommodate
proponents, species, strains, and stocking locations.


List Views
----------

A number of list views provide quick access to each of the data
elements in FSIS-II.  List views are provided for lots, stocking
events, coded wire tags, species and strain, and proponents
(hatchery).  In most cases, list views are provided in reverse
chronological order so that the most recent elements are presented
first.  Species, stocking locations and hatcheries are presented in
alphabetical order.  List views are presented in sortable, paginated
tables with some associated data for each record include a link to
detail view.  Most list views also have search box that allows users
to jump to specific records or filter the list.


Detail Views
------------

Detail views are provided for lots, stocking events, coded wire tags,
species and strain, proponents (hatchery) and stocking locations.
Detail views represent a single data element and present all of the
information in a single page.  In most cases, a table summarizing any
associated child records is included, as is a map.  In the case of
lots, the map illustrate location of associated stocking events.  In
the case of cwts, the map illustrates the location of stocking
event(s) and any subsequent recoveries.


Summary Views
-------------

Summary views are also provided for annual stocking events associated
with a specific species (and in the case of lake trout, strain).  The
summary views provide map and table associated with all of the
stocking events associated with the specified species and year.
Widgets are provided to quickly change species, strain or year.  These
views have been particularly useful when exploring stocking patterns
through time.


Spatial Queries
---------------

A form-based view is used to retrieve all of the stocking events in an
arbitrary polygon drawn on the supplied map widget by the user.  The
user can filter the resultant record-set by species if desired.
Records are returned in a paginated table in reverse chronological
order.


Data Entry Forms
----------------

Currently data entry/editing forms are disabled in FSIS-II but could
be used to add or edit fish stocking information.


Future Plans
------------

- cwt recoveries - predefined and user supplied geometries

- cwts stocked - predefined and user supplied geometries

- hatchery summaries - views for hatchery managers to verify stocking
  events associated with their facility

- common graphs and plots - standard plots might include number of
  fish stocked by region and strain thought time.


Disclaimer
---------

The data in FSIS-II should not be considered definitive.  FSIS-II
contains data cloned from provincial servers and merged with
historical stocking data.  If there are discrepancies between the
contents of FSIS-II and FSIS, FSIS should be considered correct.  A
time stamp in the footer of most pages rendered by FSIS-II indicate
when data was last downloaded from the provincial server and when
FSIS-II was last rebuild.