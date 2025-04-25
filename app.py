from flask import Flask, jsonify, request, render_template
import sqlite3
from config import DB_PATH

app = Flask(__name__)

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('instance/sqlite.db')
    conn.row_factory = sqlite3.Row 
    return conn

# Главная страница
@app.route('/')
def index():
    return render_template('/index.html')

# Маршрут для получения списка всех книг
@app.route('/books')
def books_page():
    return render_template('books.html')

# Страница со списком читателей
@app.route('/readers')
def readers_page():
    return render_template('readers.html')

# Страница выдачи и возврата книг
@app.route('/transactions')
def transactions_page():
    return render_template('transactions.html')

# Страница отчётов
@app.route('/reports')
def reports_page():
    return render_template('reports.html')

# Страница настроек
@app.route('/settings')
def settings_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    # cursor.execute('SELECT * FROM reader')
    # readers = cursor.fetchall()
    conn.close()
    return render_template('settings.html')

###############################################################################################

# API Routes

@app.route('/api/metrics')
def get_metrics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Всего книг в фонде (сумма всех quantity)
        cursor.execute('SELECT SUM(quantity) FROM book')
        total_books = cursor.fetchone()[0] or 0
        
        # 2. Книг в наличии (сумма quantity минус выданные)
        cursor.execute('''
            SELECT SUM(b.quantity) - COUNT(gb.id) 
            FROM book b
            LEFT JOIN given_book gb ON b.id = gb.book_id AND gb.return_date_fact IS NULL
        ''')
        available_books = cursor.fetchone()[0] or 0
        
        # 3. На руках у читателей
        cursor.execute('''
            SELECT COUNT(*) 
            FROM given_book 
            WHERE return_date_fact IS NULL
        ''')
        borrowed_books = cursor.fetchone()[0] or 0
        
        # 4. Требуют списания (книги с quantity <= 0)
        cursor.execute('SELECT COUNT(*) FROM book WHERE quantity <= 0')
        to_write_off = cursor.fetchone()[0] or 0
        
        # 5. Новые поступления (за последние 30 дней)
        cursor.execute('''
            SELECT COUNT(*) 
            FROM lading_bill 
            WHERE date >= date('now', '-30 days')
        ''')
        new_arrivals = cursor.fetchone()[0] or 0
        
        metrics = [
            {"title": "Всего книг в фонде", "value": f"{total_books:,}", "class": "primary"},
            {"title": "Книг в наличии", "value": f"{available_books:,}", "class": "success"},
            {"title": "На руках у читателей", "value": f"{borrowed_books:,}", "class": "info"},
            {"title": "Требуют списания", "value": f"{to_write_off:,}", "class": "warning"},
            {"title": "Новые поступления", "value": f"{new_arrivals:,}", "class": "danger"}
        ]
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        conn.close()
        
@app.route('/api/readers', methods=['POST'])
def add_reader():
    try:
        data = request.get_json()
        
        # Валидация данных
        required_fields = ['firstName', 'lastName', 'phone']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не заполнены обязательные поля"}), 400
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Вставка данных в БД
        cursor.execute('''
            INSERT INTO reader 
            (first_name, last_name, patronymic, date_birth, contact) 
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['firstName'],
            data['lastName'],
            data.get('patronymic', ''),
            data.get('birthdate', ''),
            data['phone']
        ))
        
        conn.commit()
        reader_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Читатель успешно зарегистрирован",
            "readerId": reader_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/readers', methods=['GET'])
def get_readers():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reader')
        rows = cursor.fetchall()
        
        readers = []
        for row in rows:
            readers.append({
                "id": row["id"],
                "firstName": row["first_name"],
                "lastName": row["last_name"],
                "patronymic": row["patronymic"],
                "birthdate": row["date_birth"],
                "phone": row["contact"]
            })
        
        return jsonify(readers)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        conn.close()

@app.route('/api/readers/<int:reader_id>', methods=['DELETE'])
def delete_reader(reader_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем, есть ли такой читатель в базе
        cursor.execute('SELECT * FROM reader WHERE id = ?', (reader_id,))
        reader = cursor.fetchone()
        
        if not reader:
            return jsonify({"error": "Читатель не найден"}), 404
        
        # Удаляем читателя из базы
        cursor.execute('DELETE FROM reader WHERE id = ?', (reader_id,))
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Читатель успешно удалён"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        conn.close()

@app.route('/api/readers/<int:reader_id>', methods=['GET'])
def get_reader(reader_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Устанавливаем формат строки как Row для работы с именованными столбцами
        cursor = conn.cursor()
        
        # Выполняем запрос для получения данных о читателе по ID
        cursor.execute('SELECT * FROM reader WHERE id = ?', (reader_id,))
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({"error": "Читатель не найден"}), 404
        
        # Формируем ответ с данными читателя
        reader = {
            "id": row["id"],
            "firstName": row["first_name"],
            "lastName": row["last_name"],
            "patronymic": row["patronymic"],
            "birthdate": row["date_birth"],
            "phone": row["contact"]
        }
        
        return jsonify(reader)  # Возвращаем информацию о читателе в формате JSON
        
    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке
        return jsonify({"error": str(e)}), 500
        
    finally:
        conn.close()




@app.route('/api/books', methods=['GET'])
def get_books():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                b.id, 
                b.name, 
                b.year, 
                b.quantity, 
                b.price,
                b.publishing_house,
                a.first_name || ' ' || a.last_name AS author,
                g.name AS genre
            FROM book b
            LEFT JOIN author a ON b.author_id = a.id
            LEFT JOIN genre g ON b.genre_id = g.id
        ''')

        books = cursor.fetchall()
        conn.close()

        books_list = []
        for book in books:
            print(dict(book))  # <== временная отладка
            books_list.append({
                "id": book["id"],
                "name": book["name"],
                "author": book["author"] or "—",
                "genre": book["genre"] or "—",
                "year": book["year"],
                "quantity": book["quantity"],
                "price": book["price"],
                "publishing_house": book["publishing_house"]
            })

        return jsonify(books_list)

    except Exception as e:
        print("Ошибка:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/books', methods=['POST'])
def add_book():
    try:
        data = request.get_json()

        required_fields = ['name', 'year', 'quantity', 'price', 'author_id', 'genre_id', 'publishing_house']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не заполнены обязательные поля"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO book 
            (name, year, quantity, price, author_id, genre_id, publishing_house)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['year'],
            data['quantity'],
            data['price'],
            data['author_id'],
            data['genre_id'],
            data['publishing_house']
        ))

        conn.commit()
        book_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "success": True,
            "message": "Книга успешно добавлена",
            "bookId": book_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.get_json()

        required_fields = ['name', 'year', 'quantity', 'price', 'author_id', 'genre_id', 'publishing_house']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Не заполнены обязательные поля"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем, существует ли книга
        cursor.execute('SELECT * FROM book WHERE id = ?', (book_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Книга не найдена"}), 404

        # Обновляем книгу
        cursor.execute('''
            UPDATE book
            SET name = ?, year = ?, quantity = ?, price = ?, author_id = ?, genre_id = ?, publishing_house = ?
            WHERE id = ?
        ''', (
            data['name'],
            data['year'],
            data['quantity'],
            data['price'],
            data['author_id'],
            data['genre_id'],
            data['publishing_house'],
            book_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Книга успешно обновлена"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем, существует ли книга с таким ID
        cursor.execute('SELECT * FROM book WHERE id = ?', (book_id,))
        book = cursor.fetchone()

        if not book:
            return jsonify({"error": "Книга не найдена"}), 404

        # Удаляем книгу из базы данных
        cursor.execute('DELETE FROM book WHERE id = ?', (book_id,))
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Книга успешно удалена"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)