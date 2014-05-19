drop type if exists gamestats_result;
drop type if exists gamestats_team;

create type gamestats_result as enum('draw', 'sentinel', 'scourge');
create type gamestats_team as enum('pool', 'sentinel', 'scourge', 'forbidden');

create table gamestats (
  id serial,
  result gamestats_result,
  score smallint not null default 0,
  team gamestats_team not null default 'pool',
  captain boolean not null default false,
  truanted boolean not null default false,

  room_score integer not null,
  ip inet,

  player_id integer not null,
  game_id integer not null,

  constraint "gamestats-pk" primary key (id),

  constraint "gamestats-player-fk" foreign key (player_id)
    references players (id)
    on update cascade on delete cascade,
  constraint "gamestats-game-fk" foreign key (game_id)
    references games (id)
    on update cascade on delete cascade
);
