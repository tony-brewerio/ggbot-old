create rule create_roomstats_on_player_insert as on insert to players do
  insert into roomstats(player_id, room_id) select new.id, id from rooms;
  