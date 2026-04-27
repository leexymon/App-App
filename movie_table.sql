-- Run this in your phpMyAdmin or MySQL client to create the movies table
USE `flask_db`;

CREATE TABLE IF NOT EXISTS `movies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(500) NOT NULL,
  `genres` varchar(500) DEFAULT '',
  `overview` text DEFAULT '',
  `director` varchar(255) DEFAULT '',
  `cast` text DEFAULT '',
  `release_date` varchar(20) DEFAULT '',
  `vote_average` float DEFAULT 0,
  `popularity` float DEFAULT 0,
  `runtime` float DEFAULT 0,
  `tagline` varchar(500) DEFAULT '',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
