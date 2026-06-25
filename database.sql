CREATE DATABASE notes_db;

USE notes_db;

CREATE TABLE users(

    id INT PRIMARY KEY AUTO_INCREMENT,

    username VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL

);

CREATE TABLE notes(

    id INT PRIMARY KEY AUTO_INCREMENT,

    title VARCHAR(255) NOT NULL,

    content TEXT NOT NULL,

    created_at TIMESTAMP
    DEFAULT CURRENT_TIMESTAMP,

    user_id INT,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

);