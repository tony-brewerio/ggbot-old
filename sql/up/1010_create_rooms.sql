create table rooms (
  id integer not null,
  name text not null,
  ip inet not null,

  constraint "rooms-pk" primary key (id)
);
create index "rooms-name-i" on rooms (name);