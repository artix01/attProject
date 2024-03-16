import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()


def delete(table: str, identifier: tuple[str, any]):
    """
    Удаляет запись из указанной таблицы по заданному идентификатору.

    Args:
        table (str): Имя таблицы, из которой нужно удалить запись.
        identifier (tuple): Кортеж, содержащий идентификатор для удаления записи (имя столбца и значение идентификатора).
    """
    query = f"DELETE FROM {table} WHERE {identifier[0]} = ?"

    with conn:
        cursor.execute(query, (identifier[1],))
        conn.commit()

def update(table: str, column_data: tuple[str, any], identifier: tuple[str, any]):
    """
    Обновляет данные в указанной таблице.

    Args:
        table (str): Имя таблицы, в которой нужно обновить данные.
        column_data (tuple): Кортеж, содержащий данные для обновления (новое значение и имя столбца).
        identifier (tuple): Кортеж, содержащий идентификатор для поиска записи (имя столбца и значение идентификатора).
    """
    query = f"UPDATE {table} SET {column_data[0]}=? WHERE {identifier[0]}=?"

    with conn:
        cursor.execute(query, (column_data[1], identifier[1]))
        conn.commit()

def select(table: str, columns: str, condition: str, params: tuple):
    with conn:
        cursor.execute(f"SELECT {columns} FROM {table} {condition}", params)
        return cursor.fetchall()

def insert(table: str, columns: str, data: tuple):
    quastions = ""
    for i in data:
        if quastions == "":
            quastions += "?"
        else:
            quastions += ", ?"
    print(quastions)
    query = f"INSERT INTO {table} ({columns}) VALUES ({quastions})"

    with conn:
        cursor.execute(query, data)
        conn.commit()

def is_blocked(user_id):
    """
    Проверяет, заблокирован ли пользователь.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        bool: True, если пользователь заблокирован, False в противном случае.
    """
    user_info = select("users", "status", "WHERE user_id = ?", (user_id,))[0][0]
    if user_info:
        return bool(user_info == "banned")
    else:
        return False