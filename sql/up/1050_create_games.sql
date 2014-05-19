drop type if exists games_type;
drop type if exists games_status;
drop type if exists games_winner;

create type games_type as enum('regular', 'chall');
create type games_status as enum('chall', 'fresh', 'pick', 'ongoing', 'finished');
create type games_winner as enum('draw', 'sentinel', 'scourge');

create table games (
  id serial,
  type games_type not null default 'regular',
  status games_status not null default 'fresh',
  mode text not null default '-cm'::text,
  winner games_winner not null default 'draw',
  created_at timestamp without time zone not null default now(),
  confirmed_at timestamp without time zone,
  finished_at timestamp without time zone,

  created_by_id integer,
  accepted_by_id integer,
  room_id integer not null,

  constraint "games-pk" primary key (id),

  constraint "games-created_by-fk" foreign key (created_by_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "games-accepted_by-fk" foreign key (accepted_by_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "games-room-fk" foreign key (room_id)
    references rooms (id)
    on update cascade on delete cascade
);