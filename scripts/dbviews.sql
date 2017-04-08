DROP VIEW tropheo_ngame;
DROP VIEW tropheo_gamestats;


CREATE VIEW tropheo_gamestats AS (
    SELECT platform,
        AVG(critic_score) as critic_mean,
        STDDEV_POP(critic_score) as critic_stdev,
        AVG(user_score) as user_mean,
        STDDEV_POP(user_score) as user_stdev,
        AVG(points) as points_mean,
        STDDEV_POP(points) as points_stdev
    FROM tropheo_game GROUP BY platform
    UNION
    SELECT 'all' as platform,
        AVG(critic_score) as critic_mean,
        STDDEV_POP(critic_score) as critic_stdev,
        AVG(user_score) as user_mean,
        STDDEV_POP(user_score) as user_stdev,
        AVG(points) as points_mean,
        STDDEV_POP(points) as points_stdev
    FROM tropheo_game
);

CREATE VIEW tropheo_ngame AS (
    SELECT g.id AS id,
           g.simple_id AS simple_id,
           g.title AS title,
           g.platinum AS platinum,
           g.gold AS gold,
           g.silver AS silver,
           g.bronze AS bronze,
           g.platform AS platform,
           g.points AS points,
           (g.points - s.points_mean) / s.points_stdev AS weighted_points,
           g.genre AS genre,
           g.top_genre AS top_genre,
           g.image_url AS image_url,
           g.release_date AS release_date,
           g.publisher AS publisher,
           g.maturity_rating AS maturity_rating,
           (g.critic_score - s.critic_mean) / s.critic_stdev AS critic_score,
           (g.user_score - s.user_mean) / s.user_stdev AS user_score,
           ((g.critic_score - s.critic_mean) / s.critic_stdev * 4 + (g.user_score - s.user_mean) / s.user_stdev) / 5 AS weighted_score,
           ROUND(((g.critic_score - s.critic_mean) / s.critic_stdev * 4 + (g.user_score - s.user_mean) / s.user_stdev) / 5, 2) AS score
    FROM tropheo_game AS g
    LEFT JOIN tropheo_gamestats AS s
    ON g.platform = s.platform
);
