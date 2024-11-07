CREATE TABLE `celesa` (
	`record_reference` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_unicode_ci',
	`title_text` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`person_name_inverted` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`language_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`imprint_name` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publisher_name` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publisher_id_type` INT(10) NULL DEFAULT NULL,
	`publisher_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publishing_date` DATE NULL DEFAULT NULL,
	`price_amount` DECIMAL(10,2) NULL DEFAULT NULL,
	`currency_code` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`stock` INT(10) NULL DEFAULT NULL,
	`novedad` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`idml` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`catalog_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	PRIMARY KEY (`record_reference`) USING BTREE
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;




CREATE TABLE `celesa_descuentos` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`cliente` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`nombre_cliente` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`editorial` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`nombre_editorial` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`tipo` INT(10) NULL DEFAULT NULL,
	`descripcion_tipo` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`dto` DECIMAL(5,2) NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=6440
;

CREATE TABLE `celesa_stock` (
	`isbn` VARCHAR(20) NOT NULL COLLATE 'utf8mb4_unicode_ci',
	`cnt` INT(10) NULL DEFAULT NULL,
	`last_update` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`isbn`) USING BTREE
)
COLLATE='utf8mb4_unicode_ci'
ENGINE=InnoDB
;

CREATE TABLE `meli_access` (
	`app_id` BIGINT(19) NULL DEFAULT NULL,
	`secret_key` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`country` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`access_token` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`refresh_token` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`user_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci'
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;

