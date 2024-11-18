CREATE TABLE class_term (
    class_term_id CHAR(36) PRIMARY KEY,
    title VARCHAR(64) NOT NULL,
    position INT NOT NULL,

    -- whether to display associated classes on the starting page
    start_date DATETIME
);

CREATE TABLE class (
    class_id CHAR(36) PRIMARY KEY,
    title VARCHAR(64) NOT NULL,
    class_term_id CHAR(36) NOT NULL,

    user_friendly_class_code VARCHAR(24) UNIQUE NOT NULL,

    -- the unique URL path that all pages must start with
    starting_url_path VARCHAR(128) UNIQUE NOT NULL,

    FOREIGN KEY (class_term_id) REFERENCES class_term(class_term_id)
);

CREATE TABLE user (
    user_id CHAR(36) PRIMARY KEY,
    full_name VARCHAR(64) NOT NULL,
    email VARCHAR(128) UNIQUE NOT NULL,
    -- hashed password is fixed length
    hashed_password CHAR(163) NOT NULL
);

CREATE TABLE enrollment (
    class_id CHAR(36),
    user_id VARCHAR(128),
    role INT NOT NULL,

    PRIMARY KEY (class_id, user_id),
    FOREIGN KEY (class_id) REFERENCES class(class_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE page (
    page_id CHAR(36) PRIMARY KEY,
    page_type INT NOT NULL,
    url_path VARCHAR(128) NOT NULL UNIQUE,
    page_content MEDIUMTEXT NOT NULL,
    page_title VARCHAR(256),

    class_id VARCHAR(128),
    created_by_user_id VARCHAR(128),

    FOREIGN KEY (created_by_user_id) REFERENCES user(user_id),
    FOREIGN KEY (class_id) REFERENCES class(class_id)
);

CREATE TABLE file (
    file_id VARCHAR(128) PRIMARY KEY,
    filepath VARCHAR(128) UNIQUE NOT NULL,
    uploaded_by_user_id VARCHAR(128),

    FOREIGN KEY (uploaded_by_user_id) REFERENCES user(user_id)
);

CREATE TABLE page_file_bridge (
    page_id VARCHAR(128),
    file_id VARCHAR(128),

    PRIMARY KEY (page_id, file_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id),
    FOREIGN KEY (file_id) REFERENCES file(file_id)
);

CREATE TABLE attendance_session (
    attendance_session_id VARCHAR(128) PRIMARY KEY,
    class_id VARCHAR(128),
    opening_time DATETIME NOT NULL,
    closing_time DATETIME NOT NULL,

    -- optional user-friendly title
    title VARCHAR(128),

    FOREIGN KEY (class_id) REFERENCES class(class_id)
);

CREATE TABLE attendance_record (
    user_id VARCHAR(128),
    attendance_session_id VARCHAR(128),

    PRIMARY KEY (user_id, attendance_session_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (attendance_session_id) REFERENCES attendance_session(attendance_session_id)
);