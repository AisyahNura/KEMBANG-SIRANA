CREATE DATABASE IF NOT EXISTS kembang_sirana;
USE kembang_sirana;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('admin','user') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

-- Data for users
INSERT INTO `users` (`id`, `nama`, `email`, `password`, `role`, `created_at`) VALUES (1, NULL, 'admin@sirana.com', 'admin123', 'admin', '2026-03-13 08:25:20');
INSERT INTO `users` (`id`, `nama`, `email`, `password`, `role`, `created_at`) VALUES (2, NULL, 'user@sirana.com', 'user123', 'user', '2026-03-13 08:25:20');

DROP TABLE IF EXISTS `kategori_undangan`;
CREATE TABLE `kategori_undangan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_kategori` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nama_kategori` (`nama_kategori`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

-- Data for kategori_undangan
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (1, 'ASN Kemenag', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (2, 'ASN Se-Jombang', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (3, 'Kepala KUA', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (4, 'Pengawas', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (5, 'Madrasah', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (6, 'Kepala Madrasah', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (8, 'Staff guru', 0);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (9, 'Staff kepala madrasah', 1);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (10, 'Staff KUA', 0);
INSERT INTO `kategori_undangan` (`id`, `nama_kategori`, `is_active`) VALUES (11, 'staff Kepala MAN', 1);

DROP TABLE IF EXISTS `kegiatan`;
CREATE TABLE `kegiatan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_kegiatan` varchar(200) DEFAULT NULL,
  `deskripsi` text,
  `tempat` varchar(200) DEFAULT NULL,
  `waktu` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `peserta`;
CREATE TABLE `peserta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kegiatan_id` int(11) DEFAULT NULL,
  `nama` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `instansi` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `rekaman`;
CREATE TABLE `rekaman` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kegiatan_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `uploaded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `notulensi`;
CREATE TABLE `notulensi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kegiatan_id` int(11) DEFAULT NULL,
  `rekaman_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `ringkasan` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `undangan`;
CREATE TABLE `undangan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kegiatan_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `tanggal_dibuat` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) DEFAULT NULL,
  `kegiatan` varchar(255) DEFAULT NULL,
  `tempat` varchar(255) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `waktu` time DEFAULT NULL,
  `waktu_selesai` time DEFAULT NULL,
  `peserta` text,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `catatan_admin` text,
  `email_peserta` varchar(255) DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `version` int(11) DEFAULT '1',
  `is_sent` tinyint(1) DEFAULT '0',
  `sent_at` timestamp NULL DEFAULT NULL,
  `sent_count` int(11) DEFAULT '0',
  `isi_undangan` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `undangan_history`;
CREATE TABLE `undangan_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `undangan_id` int(11) NOT NULL,
  `field_name` varchar(100) NOT NULL,
  `old_value` text,
  `new_value` text,
  `changed_by` int(11) NOT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_undangan_history_undangan_id` (`undangan_id`),
  KEY `idx_undangan_history_changed_by` (`changed_by`),
  CONSTRAINT `fk_undangan_history_undangan` FOREIGN KEY (`undangan_id`) REFERENCES `undangan` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_undangan_history_user` FOREIGN KEY (`changed_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `konfirmasi_kehadiran`;
CREATE TABLE `konfirmasi_kehadiran` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `undangan_id` int(11) NOT NULL,
  `nama` varchar(100) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `status_kehadiran` varchar(50) DEFAULT NULL,
  `waktu_konfirmasi` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `token` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `metode_konfirmasi` varchar(50) DEFAULT 'Link Website',
  `catatan` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `fk_undangan_kehadiran` (`undangan_id`),
  CONSTRAINT `fk_undangan_kehadiran` FOREIGN KEY (`undangan_id`) REFERENCES `undangan` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `master_peserta_undangan`;
CREATE TABLE `master_peserta_undangan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `nomor_hp` varchar(20) DEFAULT NULL,
  `telegram_chat_id` varchar(50) DEFAULT NULL,
  `kategori` varchar(100) NOT NULL,
  `kategori_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_kategori_penerima` (`kategori_id`),
  CONSTRAINT `fk_kategori_penerima` FOREIGN KEY (`kategori_id`) REFERENCES `kategori_undangan` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

-- Data for master_peserta_undangan
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (1, 'Andi', 'lalaaica04@gmail.com', NULL, NULL, 'ASN Kemenag', 1);
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (3, 'Evianita', 'evianita08@pens.ac.id', NULL, NULL, 'Kepala KUA', 3);
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (5, 'Amasha', 'surpiyatisantoso9@gmail.com', NULL, NULL, 'Madrasah', 5);
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (6, 'Aisyah', 'aica7992@gmail.com', NULL, NULL, 'Staff kepala madrasah', 9);
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (9, 'Aisyah', 'aisyahnuraini965@gmail.com', '-', NULL, 'Pengawas', 4);
INSERT INTO `master_peserta_undangan` (`id`, `nama`, `email`, `nomor_hp`, `telegram_chat_id`, `kategori`, `kategori_id`) VALUES (10, 'SIti', 'aicalala04@gmail.com', '087832722708', NULL, 'ASN Se-Jombang', 2);

DROP TABLE IF EXISTS `aktivitas`;
CREATE TABLE `aktivitas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `jenis_aktivitas` varchar(50) DEFAULT NULL,
  `judul` varchar(255) DEFAULT NULL,
  `tanggal_aktivitas` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

