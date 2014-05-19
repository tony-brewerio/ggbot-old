create table bans (
  id serial,
  active boolean not null default true,

  at timestamp without time zone not null default now(),
  removed_at timestamp without time zone,
  reason text not null default 'no reason'::text,
  remove_reason text default 'no reason'::text,
  by_id integer,
  removed_by_id integer,

  player_id integer not null,
  room_id integer not null,

  until timestamp without time zone,

  constraint "bans-pk" primary key (id),

  constraint "bans-by-fk" foreign key (by_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "bans-removed_by-fk" foreign key (removed_by_id)
    references players (id)
    on update cascade on delete cascade,

  constraint "bans-player-fk" foreign key (player_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "bans-room-fk" foreign key (room_id)
    references rooms (id)
    on update cascade on delete cascade
);

create index "bans-by-fki" on bans (by_id);
create index "bans-removed_by-fki" on bans (removed_by_id);
create index "bans-player-fki" on bans (player_id);
create index "bans-room-fki" on bans (room_id);
