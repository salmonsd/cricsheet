-- SQLite
with
  games as (
    select
      cast(STRFTIME('%Y', match_date) as integer) as match_year,
      file_number,
      gender
    from
      match_outcome
  ),
  strike_rate_base as (
    select
      i.file_number,
      i.batter,
      count(1) as delivery_cnt,
      sum(i.batter_runs) as total_batter_runs
    from
      innings i
    group by
      1,
      2
  ),
  strike_rate_by_year as (
    select
      g.match_year,
      srb.batter,
      g.gender,
      sum(srb.delivery_cnt) as delivery_cnt,
      sum(srb.total_batter_runs) as total_batter_runs,
      sum(srb.total_batter_runs) * 100.0 / sum(srb.delivery_cnt) as strike_rate
    from
      games g
      inner join strike_rate_base srb on g.file_number = srb.file_number
    where
      g.match_year = 2019
    group by
      1,
      2,
      3
  ),
  batter_strike_rate_pctr as (
    select
      *,
      percent_rank() over (
        partition by match_year,
        gender
        order by
          strike_rate DESC
      ) strike_rate_pctl
    from
      strike_rate_by_year
  )
select
  match_year,
  batter,
  gender,
  delivery_cnt,
  total_batter_runs,
  strike_rate
from
  batter_strike_rate_pctr
where
  strike_rate_pctl <=.05 --top 5%
order by
  gender,
  strike_rate_pctl