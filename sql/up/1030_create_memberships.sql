create table memberships (
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
  group_id integer not null,

  constraint "memberships-pk" primary key (id),

  constraint "memberships-by-fk" foreign key (by_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "memberships-removed_by-fk" foreign key (removed_by_id)
    references players (id)
    on update cascade on delete cascade,

  constraint "memberships-group-fk" foreign key (group_id)
    references groups (id)
    on update cascade on delete cascade,
  constraint "memberships-player-fk" foreign key (player_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "memberships-room-fk" foreign key (room_id)
    references rooms (id)
    on update cascade on delete cascade
);

create index "memberships-by-fki" on memberships (by_id);
create index "memberships-removed_by-fki" on memberships (removed_by_id);
create index "memberships-group-fki" on memberships (group_id);
create index "memberships-player-fki" on memberships (player_id);
create index "memberships-room-fki" on memberships (room_id);
