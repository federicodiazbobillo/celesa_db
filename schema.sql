CREATE TABLE `celesa` (
	`record_reference` VARCHAR(50) NOT NULL COLLATE 'utf8mb4_unicode_ci',
	`notification_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`product_id_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`id_value` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`product_composition` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`product_form` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`measure_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`measurement` DECIMAL(10,2) NULL DEFAULT NULL,
	`measure_unit_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`title_text` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`contributor_sequence_number` INT(10) NULL DEFAULT NULL,
	`contributor_role` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`person_name_inverted` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`language_role` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`language_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`extent_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`extent_value` INT(10) NULL DEFAULT NULL,
	`extent_unit` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`imprint_name` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publishing_role` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publisher_id_type` INT(10) NULL DEFAULT NULL,
	`publisher_id_value` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publisher_name` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publishing_status` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publishing_date` DATE NULL DEFAULT NULL,
	`supplier_role` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`supplier_name` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`product_availability` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`price_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`price_amount` DECIMAL(10,2) NULL DEFAULT NULL,
	`tax_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`tax_rate_percent` DECIMAL(5,2) NULL DEFAULT NULL,
	`currency_code` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`countries_included` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`resource_content_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`content_audience` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`resource_mode` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`resource_form` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`resource_version_feature_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`feature_value` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`resource_link` MEDIUMTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	`publisher_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8mb4_unicode_ci',
	PRIMARY KEY (`record_reference`) USING BTREE,
	UNIQUE INDEX `record_reference` (`record_reference`) USING BTREE
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
