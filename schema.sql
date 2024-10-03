-- Города
CREATE TABLE Cities (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL UNIQUE
);

-- Улицы
CREATE TABLE Streets (
    id SERIAL PRIMARY KEY,
    street VARCHAR(50) NOT NULL UNIQUE
);

-- Адреса
CREATE TABLE Addresses (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES Cities(id) ON DELETE RESTRICT,
    street_id INTEGER REFERENCES Streets(id) ON DELETE RESTRICT,
    building INTEGER
);


-- Поставщики
CREATE TABLE Vendors (
    id SERIAL PRIMARY KEY,
    inn VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    address_id INTEGER REFERENCES Addresses(id) ON DELETE RESTRICT ON UPDATE CASCADE
);


-- Товары
CREATE TABLE Products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL,
    vendor_id INTEGER REFERENCES Vendors(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    min_amount INTEGER
);


-- Контактные данные
CREATE TABLE Contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    email VARCHAR(30) NOT NULL UNIQUE,
    CONSTRAINT email_format CHECK (email ~ '^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
);

-- Точки продаж
CREATE TABLE Stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    address_id INTEGER REFERENCES Addresses(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    contacts_id INTEGER REFERENCES Contacts(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TYPE delivery_status AS ENUM ('новый', 'в обработке', 'отгружен', 'отменен');

-- Заявки на получение товара
CREATE TABLE Orders (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(10) NOT NULL, -- триггер set_document_number
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    store_id INTEGER REFERENCES Stores(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    total_sum DECIMAL(10, 2) NOT NULL, -- возможно, это значение будет вычисляться триггером
    status delivery_status NOT NULL DEFAULT 'новый'
);

-- Позиции заказов
CREATE TABLE Order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES Orders(id) ON DELETE CASCADE ON UPDATE CASCADE,
    product_id INTEGER REFERENCES Products(id) ON DELETE CASCADE ON UPDATE CASCADE,
    amount INTEGER DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.0
);

-- Накладные
CREATE TABLE Invoices (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES Stores(id) ON DELETE CASCADE ON UPDATE CASCADE,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status delivery_status NOT NULL DEFAULT 'отгружен',
    order_items JSONB NOT NULL -- для хранения списка товаров
);


-- Отгрузки
CREATE TABLE Supplies (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES Products(id) ON DELETE CASCADE ON UPDATE CASCADE,
    amount INTEGER NOT NULL,
    supply_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Логи
CREATE TABLE Action_logs (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    table_name VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,    -- Тип действия (INSERT, UPDATE, DELETE)
    row_id INTEGER,                 -- Идентификатор строки, над которой произведено действие
    old_data JSONB,                 -- Данные до изменения (для UPDATE и DELETE)
    new_data JSONB,                 -- Данные после изменения (для INSERT и UPDATE)
    user_id INTEGER -- Идентификатор пользователя (если реализована система пользователей)
);



-- Индексы
-- Повышение производительности для больших объемы данных
CREATE INDEX idx_inn ON Vendors(inn);
CREATE INDEX idx_email ON Contacts(email);
CREATE INDEX idx_address_id ON Stores(address_id);
CREATE INDEX idx_contact_id ON Stores(contacts_id);
CREATE INDEX id_order_id ON Order_items(order_id);
CREATE INDEX id_product_id ON Order_items(product_id);


-- Индексы на полях action_time, table_name, и row_id выбираются, потому что они чаще всего используются для фильтрации и анализа данных в логах.
CREATE INDEX idx_action_time ON Action_logs(action_time); -- ускоряет запросы поиска по времени
CREATE INDEX idx_table_name ON Action_logs(table_name); -- ускоряет запросы, которые фильтруют данные по таблицам
CREATE INDEX idx_row_id ON Action_logs(row_id); -- ускоряет запросы поиска действий по конкретной записи (строке) в таблице




-- Триггеры
-- 1. Генерировать номер документа
-- 1. Генерация номера документа
CREATE SEQUENCE document_number_seq;

CREATE OR REPLACE FUNCTION generate_document_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.document_number := 'DOC-' || NEXTVAL('document_number_seq');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_document_number
BEFORE INSERT ON Orders
FOR EACH ROW EXECUTE FUNCTION generate_document_number();


-- 2. Вычисление полной суммы заказа
CREATE OR REPLACE FUNCTION calculate_total_sum()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Orders
    SET total_sum = (SELECT COALESCE(SUM(amount * price), 0) FROM Order_items WHERE order_id = NEW.order_id)
    WHERE id = NEW.order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_total_sum
AFTER INSERT OR UPDATE ON Order_items
FOR EACH ROW EXECUTE FUNCTION calculate_total_sum();


-- 3. Запись в лог активности
CREATE OR REPLACE FUNCTION log_product_actions()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO Action_logs(table_name, action, row_id, new_data)
        VALUES('Products', 'INSERT', NEW.id, row_to_json(NEW));

    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO Action_logs(table_name, action, row_id, old_data, new_data)
        VALUES('Products', 'UPDATE', OLD.id, row_to_json(OLD), row_to_json(NEW));

    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO Action_logs(table_name, action, row_id, old_data)
        VALUES('Products', 'DELETE', OLD.id, row_to_json(OLD));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER product_log_trigger
AFTER INSERT OR UPDATE OR DELETE ON Products
FOR EACH ROW EXECUTE FUNCTION log_product_actions();


-- 4. Автоматическое изменение статуса отгрузки товара
CREATE OR REPLACE FUNCTION update_invoice_status()
RETURNS TRIGGER AS $$
DECLARE
    total_items INTEGER;
    shipped_items INTEGER;
BEGIN
    -- 1. Считаем общее количество товаров в заказе
    SELECT COUNT(*) INTO total_items FROM Order_items WHERE order_id = NEW.order_id;

    -- 2. Считаем количество товаров, которые были отгружены (amount > 0)
    SELECT COUNT(*) INTO shipped_items FROM Order_items WHERE order_id = NEW.order_id AND amount > 0;

    -- 3. Если все товары отгружены, меняем статус на "отгружен"
    IF shipped_items = total_items THEN
        UPDATE Invoices SET status = 'отгружен' WHERE order_id = NEW.order_id;

    -- 4. Если хотя бы один товар отгружен, но не все, меняем статус на "в обработке"
    ELSIF shipped_items > 0 THEN
        UPDATE Invoices SET status = 'в обработке' WHERE order_id = NEW.order_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_product_insert
AFTER INSERT OR UPDATE ON Order_items
FOR EACH ROW EXECUTE FUNCTION update_invoice_status();
