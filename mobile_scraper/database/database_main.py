import psycopg2
from mobile_scraper.database.config import host, user, password, db_name


# получение соеднения с БД
def get_connection_to_db():
    try:
        # соединение с существующей базой данных
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        connection.autocommit = True
        print("[PostGreSQL INFO] Connected successfully")
        return connection
    except Exception as _ex:
        print("[PostGreSQL INFO] Error while working with PostgreSQL", _ex)
        return None


# создание/обновление таблицы моделей в БД
def update_models_table_to_db(models_data):
    # получаем соединение
    connection = get_connection_to_db()

    # если соединение установлено успешно
    if connection:
        with connection.cursor() as cursor:
            # проверка на существование таблицы
            table_name = "vehicles_models"
            cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname=%s)", (table_name,))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                # если таблица существует - удаляем все данные перед записью
                cursor.execute(f"DELETE FROM {table_name};")
            else:
                # иначе создаём новую таблицу
                cursor.execute(f"CREATE TABLE {table_name}(id serial PRIMARY KEY, producer varchar(255) NOT NULL,"
                               f"model varchar(255) NOT NULL, model_id int, url varchar(511));")

            # запись в БД с кодировкой в ascii
            for tmp in range(len(models_data["Producer"])):
                # кодировка в ASCII для последующей записи в таблице
                producer = ascii(models_data['Producer'][tmp])[1:-1]
                model = ascii(models_data['Models'][tmp])[1:-1]
                model_id = ascii(models_data['ModelID'][tmp])[1:-1]
                url = ascii(models_data['URL'][tmp])[1:-1]

                # print((producer, model, model_id, url))

                # SQL запрос
                query = "INSERT INTO vehicles_models (producer, model, model_id, url) VALUES (%s, %s, %s, %s)"
                print(query, (producer, model, model_id, url))
                cursor.execute(query, (producer, model, model_id, url))

        connection.commit()
        # прикрываем соединение
        connection.close()
        print("[PostGreSQL INFO] Connection closed")
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")


def read_models_from_db():
    # получаем соединение
    connection = get_connection_to_db()

    # если соединение установлено успешно
    if connection:
        with connection.cursor() as cursor:
            # проверка на существование таблицы
            table_name = "vehicles_models"
            cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname=%s)", (table_name,))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                producers_li = []
                models_li = []

                # получение марок из БД
                cursor.execute(
                    "SELECT producer from vehicles_models;"
                )
                for producer_string in cursor.fetchall():
                    producers_li.append(bytes(producer_string[0], 'utf-8').decode('unicode_escape'))

                # получение моделей из БД
                cursor.execute(
                    "SELECT model from vehicles_models;"
                )
                for models_string in cursor.fetchall():
                    models_li.append(bytes(models_string[0], 'utf-8').decode('unicode_escape'))

                # инициализация словаря формата - модель: [марка_модели1, марка_модели2, ...]
                producers_models_data = {producer: [] for producer in set(producers_li)}

                # заполнение словаря моделями
                for indx in range(len(producers_li)):
                    producers_models_data[producers_li[indx]].append(models_li[indx])

                print("[PostGreSQL INFO] Data was read successfully.")

            else:
                print(f"[PostGreSQL INFO] Error while trying to read {table_name}. {table_name} doesn't exist.")
                connection.close()
                return None

        connection.commit()
        # прикрываем соединение
        connection.close()
        print("[PostGreSQL INFO] Connection closed")

        return producers_models_data
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")
