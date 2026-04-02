CREATE DATABASE IF NOT EXISTS sirana_kembang;
USE sirana_kembang;

CREATE TABLE IF NOT EXISTS undangan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kegiatan VARCHAR(255) NOT NULL,
    tempat VARCHAR(255) NOT NULL,
    tanggal DATE NOT NULL,
    waktu TIME NOT NULL,
    peserta TEXT NOT NULL,
    anggaran VARCHAR(100) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by VARCHAR(100) NULL,
    approved_at TIMESTAMP NULL
);