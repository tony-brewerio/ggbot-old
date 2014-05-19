
create table accounts (
  id integer not null,
  login text not null,
  packet text not null,

  constraint "accounts-pk" primary key (id)
);
