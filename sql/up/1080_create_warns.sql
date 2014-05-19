drop type if exists warns_type;

create type warns_type as enum('truant', 'noob', 'censure',
  'serious violation', 'misc violation');

create table warns (
  id serial,
  active boolean not null default true,
  type warns_type not null,

  at timestamp without time zone not null default now(),
  removed_at timestamp without time zone,
  reason text not null default 'no reason'::text,
  remove_reason text default 'no reason'::text,
  by_id integer,
  removed_by_id integer,

  player_id integer not null,
  room_id integer not null,
  game_id integer,

  constraint "warns-pk" primary key (id),

  constraint "warns-by-fk" foreign key (by_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "warns-removed_by-fk" foreign key (removed_by_id)
    references players (id)
    on update cascade on delete cascade,

  constraint "warns-player-fk" foreign key (player_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "warns-room-fk" foreign key (room_id)
    references rooms (id)
    on update cascade on delete cascade,
  constraint "warns-game-fk" foreign key (game_id)
    references games (id)
    on update cascade on delete cascade
);

create index "warns-by-fki" on warns (by_id);
create index "warns-removed_by-fki" on warns (removed_by_id);
create index "warns-player-fki" on warns (player_id);
create index "warns-room-fki" on warns (room_id);
create index "warns-game-fki" on warns (game_id);
