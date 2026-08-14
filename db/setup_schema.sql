BEGIN;

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. MASTER DATA: CATEGORY
-- ==========================================
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS purchasing CASCADE;
DROP TABLE IF EXISTS stock_opname CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS material CASCADE;
DROP TABLE IF EXISTS location CASCADE;
DROP TABLE IF EXISTS category CASCADE;

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. MASTER DATA: LOCATION
-- ==========================================
CREATE TABLE location (
    location_id SERIAL PRIMARY KEY,
    location_code VARCHAR(50) NOT NULL UNIQUE,
    location_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 3. MASTER DATA: MATERIAL
-- ==========================================
CREATE TABLE material (
    material_id SERIAL PRIMARY KEY,
    material_code VARCHAR(50) NOT NULL UNIQUE,
    material_name VARCHAR(150) NOT NULL,
    category_id INT REFERENCES category(category_id) ON DELETE SET NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'PCS',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 4. INVENTORY (STOCK BALANCE & OPNAME)
-- ==========================================
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    material_id INT NOT NULL REFERENCES material(material_id) ON DELETE RESTRICT,
    location_id INT NOT NULL REFERENCES location(location_id) ON DELETE RESTRICT,
    stock_qty NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_material_location UNIQUE (material_id, location_id)
);

CREATE TABLE stock_opname (
    opname_id SERIAL PRIMARY KEY,
    material_id INT NOT NULL REFERENCES material(material_id) ON DELETE RESTRICT,
    location_id INT NOT NULL REFERENCES location(location_id) ON DELETE RESTRICT,
    system_qty NUMERIC(12, 2) NOT NULL,
    actual_qty NUMERIC(12, 2) NOT NULL,
    difference_qty NUMERIC(12, 2) NOT NULL,
    stock_opname_date DATE NOT NULL DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 5. PURCHASING
-- ==========================================
CREATE TABLE purchasing (
    purchase_id SERIAL PRIMARY KEY,
    purchase_number VARCHAR(50) NOT NULL UNIQUE,
    material_id INT NOT NULL REFERENCES material(material_id) ON DELETE RESTRICT,
    location_id INT NOT NULL REFERENCES location(location_id) ON DELETE RESTRICT,
    quantity NUMERIC(12, 2) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(15, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(15, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 6. SALES
-- ==========================================
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    sales_number VARCHAR(50) NOT NULL UNIQUE,
    material_id INT NOT NULL REFERENCES material(material_id) ON DELETE RESTRICT,
    location_id INT NOT NULL REFERENCES location(location_id) ON DELETE RESTRICT,
    quantity NUMERIC(12, 2) NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(15, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(15, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    sales_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 7. AUTOMATED UPDATED_AT TIMESTAMP TRIGGER
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_category_modtime BEFORE UPDATE ON category FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_location_modtime BEFORE UPDATE ON location FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_material_modtime BEFORE UPDATE ON material FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_modtime BEFORE UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_stock_opname_modtime BEFORE UPDATE ON stock_opname FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_purchasing_modtime BEFORE UPDATE ON purchasing FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sales_modtime BEFORE UPDATE ON sales FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;