CREATE OR REPLACE FUNCTION merge_players(old_id integer, new_id integer)
  RETURNS void AS
$BODY$
declare
  update_table text;
  update_column text;
  query text;
begin
  -- at first, we delete all the new_id's roomstats, so they won't interfere
  delete from roomstats where player_id = new_id;

  -- we also want to remove all the new_id's personal active memberships
  delete from memberships where active and player_id = new_id;

  -- and now, we update all of the foreign keys, pointing to players.id
  for update_table, update_column in select
      kcu.table_name, kcu.column_name
    from
      information_schema.constraint_column_usage ccu,
      information_schema.key_column_usage kcu
    where
      ccu.constraint_name = kcu.constraint_name
      and ccu.table_name = 'players' and ccu.column_name = 'id'
      and kcu.table_name <> 'players' loop

    execute 'update ' || update_table || ' set ' || update_column || ' = ' || new_id
      || ' where ' || update_column || ' = ' || old_id || ';';

  end loop;

  -- oh, and finally, our old_player whould be no more :)
  delete from players where id = old_id;
end;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE;
