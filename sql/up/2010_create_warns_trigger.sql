create or replace function
  warn_update_player_score(warn_type text, _player_id integer, _room_id integer, direction integer)
  returns void AS
$body$

  declare
    score_delta integer;
  begin
    select
      case
        when warn_type = 'truant' then 100
        when warn_type = 'serious violation' then 80
        when warn_type = 'misc violation' then 60
        when warn_type = 'noob' then 40
        else 20 -- censure
      end
      into score_delta;

    update roomstats set score = score + score_delta * direction
      where room_id = _room_id and player_id = _player_id;

  end;

$body$
language "plpgsql";





create or replace rule warns_on_insert as on insert to warns do
  select warn_update_player_score(new.type::text, new.player_id, new.room_id, -1);

create or replace rule warns_on_update as on update to warns do
  select warn_update_player_score(new.type::text, new.player_id, new.room_id,
    case
      when old.active = true and new.active = false then 1
      when old.active = false and new.active = true then -1
      else 0 -- anything can happen, no?
    end);
