create table groups (
  id serial,
  name text not null,

  constraint "groups-pk" primary key (id)
);
create index "groups-name-i" on groups (name);
