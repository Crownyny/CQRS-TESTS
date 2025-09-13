-- Script de migración para insertar 1 millón de registros
-- V2_0__Insert_Million_Records.sql

-- Insertar posts (100,000 registros)
INSERT INTO cqrs.post (content)
SELECT 'Content for post number ' || generate_series(1, 100000);

-- Insertar comentarios (500,000 registros - 5 comentarios por post en promedio)
WITH post_ids AS (
    SELECT id FROM cqrs.post
)
INSERT INTO cqrs.comment (content, post_id)
SELECT 
    'Comment content for comment number ' || generate_series(1, 5),
    p.id
FROM post_ids p
CROSS JOIN generate_series(1, 5);

-- Insertar reacciones (400,000 registros)
WITH comment_ids AS (
    SELECT id FROM cqrs.comment LIMIT 100000
),
emojis AS (
    SELECT unnest(ARRAY['😀', '😂', '❤️', '👍', '😢', '😡', '🎉', '🔥']) as emoji
)
INSERT INTO cqrs.comment_reaction (emoji, comment_id)
SELECT 
    e.emoji,
    c.id
FROM comment_ids c
CROSS JOIN emojis e
WHERE random() < 0.5; -- Aproximadamente 50% de probabilidad de inserción

-- Análisis de registros creados
DO $$ 
DECLARE 
    post_count INTEGER;
    comment_count INTEGER;
    reaction_count INTEGER;
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO post_count FROM cqrs.post;
    SELECT COUNT(*) INTO comment_count FROM cqrs.comment;
    SELECT COUNT(*) INTO reaction_count FROM cqrs.comment_reaction;
    total_count := post_count + comment_count + reaction_count;
    
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'Posts created: %', post_count;
    RAISE NOTICE 'Comments created: %', comment_count;
    RAISE NOTICE 'Reactions created: %', reaction_count;
    RAISE NOTICE 'Total records inserted: %', total_count;
    
    IF total_count >= 1000000 THEN
        RAISE NOTICE 'SUCCESS: Over 1 million records created!';
    ELSE
        RAISE NOTICE 'INFO: % records created (target was 1 million)', total_count;
    END IF;
END $$;
