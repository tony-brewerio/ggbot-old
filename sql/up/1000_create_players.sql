
create table players (
  id integer not null,
  login text not null,

  constraint "players-pk" primary key (id)
);

create index "players-login-i" on players (login);
