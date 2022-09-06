-- SQLite
with
  year_teams as (
    select
      distinct cast(STRFTIME('%Y', match_date) as integer) as match_year,
      team_1 as team,
      gender
    from
      match_outcome
    union
    select
      distinct cast(STRFTIME('%Y', match_date) as integer) as match_year,
      team_2 as team,
      gender
    from
      match_outcome
  ),
  games_base as (
    select
      cast(STRFTIME('%Y', match_date) as integer) as match_year,
      gender,
      team_1,
      team_2,
      1 as game_played
    from
      match_outcome
    where
      winner is not null
  ),
  games_played as (
    select
      yt.match_year,
      yt.team,
      yt.gender,
      sum(gb.game_played) as games_played
    from
      year_teams yt
      left join games_base gb on yt.match_year = gb.match_year
      and yt.gender = gb.gender
      and (
        yt.team = gb.team_1
        or yt.team = gb.team_2
      )
    group by
      1,
      2,
      3
  ),
  games_won as (
    select
      STRFTIME('%Y', match_date) as match_year,
      winner as team,
      gender,
      count(1) as games_won
    from
      match_outcome
    where
      winner is not null
    group by
      1,
      2,
      3
  ),
  games_pct as (
    select
      gp.match_year,
      gp.team,
      gp.gender,
      coalesce(gw.games_won, 0) as games_won,
      ROUND(coalesce(gw.games_won, 0) * 1.0 / gp.games_played, 4) as win_pct
    from
      games_played gp
      left join games_won gw on gp.match_year = gw.match_year
      and gp.team = gw.team
      and gp.gender = gw.gender
  ),
  win_rank_by_year as (
    select
      *,
      rank() over (
        partition by match_year,
        gender
        order by
          win_pct DESC
      ) win_pct_rank
    from
      games_pct
  )
select
  *
from
  win_rank_by_year
where
  match_year = 2019
  and win_pct_rank = 1