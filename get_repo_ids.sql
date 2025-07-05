-- Simple query to get repository IDs with language data
SELECT DISTINCT 
    r.repo_id,
    r.repo_name,
    rg.rg_name as organization,
    COUNT(DISTINCT erl.programming_language) as languages
FROM repo r
JOIN repo_groups rg ON r.repo_group_id = rg.repo_group_id
JOIN explorer_repo_languages erl ON r.repo_id = erl.repo_id
GROUP BY r.repo_id, r.repo_name, rg.rg_name
ORDER BY languages DESC
LIMIT 10;
