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
        print("[PostGreSQL INFO] Connected successfully.")
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
        print("[PostGreSQL INFO] Connection closed.")
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")


# получение словаря с моделями из БД
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
        print("[PostGreSQL INFO] Connection closed.")

        return producers_models_data
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")
        return None


# чтение локальных ссылок из БЛ
def get_local_links_from_db():
    # получаем соединение
    connection = get_connection_to_db()

    # если соединение установлено успешно
    if connection:
        with connection.cursor() as cursor:
            # проверка на существование таблицы
            table_name = "vehicles_data"
            cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname=%s)", (table_name,))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                locals_li = []

                # получение марок из БД
                cursor.execute(
                    "SELECT source_url from vehicles_data;"
                )
                for local_url in cursor.fetchall():
                    locals_li.append(bytes(local_url[0], 'utf-8').decode('unicode_escape'))

                print("[PostGreSQL INFO] Data was read successfully.")

            else:
                print(f"[PostGreSQL INFO] Error while trying to read {table_name}. {table_name} doesn't exist.")
                connection.close()
                return None

        connection.commit()
        # прикрываем соединение
        connection.close()
        print("[PostGreSQL INFO] Connection closed.")
        return locals_li
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")
        return None


# запись данных машины в БД
def write_productdata_to_db(product_data):
    # получаем соединение
    connection = get_connection_to_db()

    # запись в БД с кодировкой в ascii
    # если соединение установлено успешно
    if connection:
        with connection.cursor() as cursor:

            # ОСНОВНАЯ ИНФОРМАЦИЯ
            name = ascii(product_data['Title'])[1:-1]
            url = ascii(product_data['URL'])[1:-1]
            brutto_price = ascii(product_data['BruttoPrice'])[1:-1]
            netto_price = ascii(product_data['NettoPrice'])[1:-1]

            # ПРОИЗВОДИТЕЛЬ И МОДЕЛЬ
            all_models_dict = read_models_from_db()
            product_make = ' '
            product_model = ' '

            for make in all_models_dict:
                if make in product_data['Title']:
                    product_make = ascii(make)[1:-1]
                    for model in all_models_dict[make]:
                        if model in product_data['Title']:
                            product_model = ascii(model)[1:-1]

            # ПОБОЧКА
            characteristics = ascii(product_data['CharacteristicsStr'])[1:-1]
            description = ascii(product_data['DescriptionStr'])[1:-1]

            dealer_name = ascii(product_data['DealerData'][0])[1:-1]
            dealer_url = ascii(product_data['DealerData'][1])[1:-1]
            dealer_phone = ascii(product_data['DealerData'][2])[1:-1]

            # ИЗОБРАЖЕНИЯ
            img1 = img2 = img3 = img4 = img5 = img6 = img7 = img8 = img9 = img10 = img11 = img12 = img13 = img14 \
                = img15 = ''

            if len(product_data['ImgLi']) >= 1:
                img1 = ascii([product_data['ImgLi'][0]])[1:-1]
            if len(product_data['ImgLi']) >= 2:
                img2 = ascii([product_data['ImgLi'][1]])[1:-1]
            if len(product_data['ImgLi']) >= 3:
                img3 = ascii([product_data['ImgLi'][2]])[1:-1]
            if len(product_data['ImgLi']) >= 4:
                img4 = ascii([product_data['ImgLi'][3]])[1:-1]
            if len(product_data['ImgLi']) >= 5:
                img5 = ascii([product_data['ImgLi'][4]])[1:-1]
            if len(product_data['ImgLi']) >= 6:
                img6 = ascii([product_data['ImgLi'][5]])[1:-1]
            if len(product_data['ImgLi']) >= 7:
                img7 = ascii([product_data['ImgLi'][6]])[1:-1]
            if len(product_data['ImgLi']) >= 8:
                img8 = ascii([product_data['ImgLi'][7]])[1:-1]
            if len(product_data['ImgLi']) >= 9:
                img9 = ascii([product_data['ImgLi'][8]])[1:-1]
            if len(product_data['ImgLi']) >= 10:
                img10 = ascii([product_data['ImgLi'][9]])[1:-1]
            if len(product_data['ImgLi']) >= 11:
                img11 = ascii([product_data['ImgLi'][10]])[1:-1]
            if len(product_data['ImgLi']) >= 12:
                img12 = ascii([product_data['ImgLi'][11]])[1:-1]
            if len(product_data['ImgLi']) >= 13:
                img13 = ascii([product_data['ImgLi'][12]])[1:-1]
            if len(product_data['ImgLi']) >= 14:
                img14 = ascii([product_data['ImgLi'][13]])[1:-1]
            if len(product_data['ImgLi']) >= 15:
                img15 = ascii([product_data['ImgLi'][14]])[1:-1]

            # КАТЕГОРИИ
            techopt = product_data['TechOptDict']
            category1 = category2 = category3 = category4 = category5 = category6 = category7 = category8 = \
                category9 = category10 = category11 = category12 = category13 = category14 = category15 = category16 \
                = category17 = category18 = category19 = category20 = category21 = category22 = category23 = ''

            if 'Категория' in techopt:
                category1 = ascii(techopt['Категория'])[1:-1]
            if 'Первая регистрация' in techopt:
                category2 = ascii(techopt['Первая регистрация'])[1:-1]
            if 'Коробка передач' in techopt:
                category3 = ascii(techopt['Коробка передач'])[1:-1]
            if 'Топливо' in techopt:
                category4 = ascii(techopt['Топливо'])[1:-1]
            if 'Пробег' in techopt:
                category5 = ascii(techopt['Пробег'])[1:-1]
            if 'Мощность' in techopt:
                category6 = ascii(techopt['Мощность'])[1:-1]
            if 'Объем двигателя' in techopt:
                category7 = ascii(techopt['Объем двигателя'])[1:-1]
            if 'Количество мест' in techopt:
                category8 = ascii(techopt['Количество мест'])[1:-1]
            if 'Число дверей' in techopt:
                category9 = ascii(techopt['Число дверей'])[1:-1]
            if 'Класс экологической безопасности' in techopt:
                category10 = ascii(techopt['Класс экологической безопасности'])[1:-1]
            if 'Количество владельцев транспортного средства' in techopt:
                category11 = ascii(techopt['Количество владельцев транспортного средства'])[1:-1]
            if 'Общий осмотр' in techopt:
                category12 = ascii(techopt['Общий осмотр'])[1:-1]
            if 'Цвет' in techopt:
                category13 = ascii(techopt['Цвет'])[1:-1]
            if 'Цвет по классификации производителя' in techopt:
                category14 = ascii(techopt['Цвет по классификации производителя'])[1:-1]
            if 'Состояние транспортного средства' in techopt:
                category15 = ascii(techopt['Состояние транспортного средства'])[1:-1]
            if 'Оригинал' in techopt:
                category16 = ascii(techopt['Оригинал'])[1:-1]
            if 'Потребление' in techopt:
                category17 = ascii(techopt['Потребление'])[1:-1]
            if 'CO₂ Emissions' in techopt:
                category18 = ascii(techopt['CO₂ Emissions'])[1:-1]
            if 'Датчики парковки' in techopt:
                category19 = ascii(techopt['Датчики парковки'])[1:-1]
            if 'Дизайн салона' in techopt:
                category20 = ascii(techopt['Дизайн салона'])[1:-1]
            if 'Номер транспортного средства' in techopt:
                category21 = ascii(techopt['Номер транспортного средства'])[1:-1]
            if 'Наличие' in techopt:
                category22 = ascii(techopt['Наличие'])[1:-1]
            if 'Вид основного топлива' in techopt:
                category23 = ascii(techopt['Вид основного топлива'])[1:-1]

            # SQL запрос
            query = "INSERT INTO vehicles_data (name, make, model, source_url, price_brutto, price_netto, " \
                    "characteristics, description, dealer_name, dealer_url, dealer_phone, img1, img2, img3, img4, " \
                    "img5, img6, img7, img8, img9, img10, img11, img12, img13, img14, img15, category1, category2," \
                    " category3, category4, category5, category6, category7, category8, category9, category10," \
                    " category11, category12, category13, category14, category15, category16, category17," \
                    " category18, category19, category20, category21, category22, category23)" \
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s," \
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s)"

            cursor.execute(query, (name, product_make, product_model, url, brutto_price, netto_price, characteristics,
                                   description, dealer_name, dealer_url, dealer_phone, img1, img2, img3, img4, img5,
                                   img6, img7, img8, img9, img10, img11, img12, img13, img14, img15, category1,
                                   category2, category3, category4, category5, category6, category7, category8,
                                   category9, category10,  category11, category12, category13, category14, category15,
                                   category16, category17, category18, category19, category20, category21, category22,
                                   category23))
            print("[PostGreSQL INFO] Data was wrote to DataBase.")
        connection.commit()
        # прикрываем соединение
        connection.close()
        print("[PostGreSQL INFO] Connection closed.")
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")


# отмечает товар неактивым в БД по его сслыке
def edit_product_activity_in_db(local_link):
    # получаем соединение
    connection = get_connection_to_db()

    # если соединение установлено успешно
    if connection:
        with connection.cursor() as cursor:
            # проверка на существование таблицы
            table_name = "vehicles_data"
            cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname=%s)", (table_name,))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                locals_li = []

                # отметка товара неактивным в БД
                cursor.execute(
                    "UPDATE vehicles_data SET activity = false WHERE source_url = "
                    f"'{local_link}';"
                )
                # установка даты, с которой товар стал неактивен в БД
                cursor.execute(
                        "DELETE FROM vehicles_data WHERE unactive_since <= NOW() - INTERVAL '1 day';"
                )

            else:
                print(f"[PostGreSQL INFO] Error while trying to read {table_name}. {table_name} doesn't exist.")
                connection.close()
                return None

        connection.commit()
        # прикрываем соединение
        connection.close()
        print("[PostGreSQL INFO] Connection closed.")
        return locals_li
    else:
        print("[PostGreSQL INFO] Error, couldn't get connection...")
        return None
