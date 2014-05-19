create table roomstats (
  id serial,
  score integer not null default 1000,
  streak smallint not null default 0,
  wins integer not null default 0,
  loses integer not null default 0,

  player_id integer not null,
  room_id integer not null,

  constraint "roomstats-pk" primary key (id),

  constraint "roomstats-player-fk" foreign key (player_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "roomstats-room-fk" foreign key (room_id)
    references rooms (id)
    on update cascade on delete cascade
);
create index "roomstats-player-fki" on roomstats (player_id);
create index "roomstats-room-fki" on roomstats (room_id);