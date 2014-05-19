
insert into public.groups(name) values
  ('player'),
  ('leader'), ('veteran'), ('host'),
  ('gm'), ('guard'), ('voucher'),
  ('moder'), ('admin');

insert into public.rooms(id, ip, name) values
  (1245024, '67.228.162.188', '0SPL-Allstars Slaves Room'),
  (1245025, '67.228.162.188', '0SPL-Allstars Mortals Room'),
  (1245026, '67.228.162.188', '0SPL-Allstars Gods Room');

insert into public.players(id, login) values
  (1,  'fareko'),
  (2,  'puma'),
  (3,  'gaylord'),
  (4,  'masyoka'),
  (5,  'love'),
  (6,  'imbamania'),
  (7,  'woody'),
  (8,  'zgay'),
  (9,  'spock'),
  (10, 'lucky'),
  (11, 'papaDray'),
  (12, 'twik');

update public.roomstats set score = round(random() * 1000 + 1000);

insert into public.memberships(reason, player_id, room_id, group_id) values
  ('::default::',
    (select id from players where login = 'fareko'),
    1245024,
    (select id from groups where name = 'admin'));


insert into public.memberships(reason, player_id, room_id, group_id)
  select '::default::', id, 1245024, (select id from groups where name = 'host')
    from players where login in ('lucky', 'twik');

insert into public.memberships(reason, player_id, room_id, group_id)
  select '::default::', id, 1245024, (select id from groups where name = 'voucher')
    from players where login in ('fareko', 'twik', 'woody');

insert into public.memberships(reason, player_id, room_id, group_id)
  select '::default::', id, 1245024, (select id from groups where name = 'leader')
    from players where login in ('papaDray', 'imbamania', 'twik');

insert into public.memberships(reason, player_id, room_id, group_id)
  select '::default::', id, 1245024, (select id from groups where name = 'player')
    from players where login <> 'gaylord';
