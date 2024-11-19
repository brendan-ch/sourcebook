-- Tables
CREATE TABLE course_term (
    course_term_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(64) NOT NULL,
    position INT NOT NULL,

    -- whether to display associated classes on the starting page
    start_date DATETIME
);

CREATE TABLE course (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(64) NOT NULL,
    course_term_id INT,

    user_friendly_class_code VARCHAR(24) UNIQUE NOT NULL,

    -- the unique URL path that all pages must start with
    starting_url_path VARCHAR(128) UNIQUE NOT NULL,

    FOREIGN KEY (course_term_id) REFERENCES course_term(course_term_id)
);

CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(64) NOT NULL,
    email VARCHAR(128) UNIQUE NOT NULL,
    -- hashed password is fixed length
    hashed_password CHAR(163) NOT NULL
);

CREATE TABLE enrollment (
    course_id INT NOT NULL,
    user_id INT NOT NULL,
    role INT NOT NULL,

    PRIMARY KEY (course_id, user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE page (
    page_id INT PRIMARY KEY AUTO_INCREMENT,
    page_type INT NOT NULL,
    url_path VARCHAR(128) NOT NULL UNIQUE,
    page_content MEDIUMTEXT NOT NULL,
    page_title VARCHAR(256),

    course_id INT,
    created_by_user_id INT,

    FOREIGN KEY (created_by_user_id) REFERENCES user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE file (
    file_id INT PRIMARY KEY AUTO_INCREMENT,
    filepath VARCHAR(128) UNIQUE NOT NULL,
    uploaded_by_user_id INT,

    FOREIGN KEY (uploaded_by_user_id) REFERENCES user(user_id)
);

CREATE TABLE page_file_bridge (
    page_id INT,
    file_id INT,

    PRIMARY KEY (page_id, file_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id),
    FOREIGN KEY (file_id) REFERENCES file(file_id)
);

CREATE TABLE attendance_session (
    attendance_session_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT,
    opening_time DATETIME NOT NULL,
    closing_time DATETIME NOT NULL,

    -- optional user-friendly title
    title VARCHAR(128),

    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE attendance_record (
    user_id INT,
    attendance_session_id INT,

    PRIMARY KEY (user_id, attendance_session_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (attendance_session_id) REFERENCES attendance_session(attendance_session_id)
);

