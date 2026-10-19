echo "Creating select user..."
psql -v ON_ERROR_STOP=1 --username "$DB_super_user_name" --dbname "$DB_name" <<-EOSQL
--Создание select_user.
CREATE ROLE "$DB_select_user_name" WITH LOGIN PASSWORD '$DB_select_user_password';
--Дает права на чтение существующих таблиц.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$DB_select_user_name";
--Дает права на чтение таблиц, которые будут созданы позднее.
ALTER DEFAULT PRIVILEGES FOR ROLE "$DB_super_user_name" IN SCHEMA public GRANT SELECT ON TABLES TO "$DB_select_user_name";
EOSQL
