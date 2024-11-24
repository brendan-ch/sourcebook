CREATE SCHEMA sourcebook;
USE sourcebook;

CREATE TABLE IF NOT EXISTS course_term (
    course_term_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(64) NOT NULL,
    position_from_top INT NOT NULL
);

CREATE TABLE IF NOT EXISTS course (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(64) NOT NULL,
    course_term_id INT,
    user_friendly_class_code VARCHAR(24) NOT NULL,

    -- the unique URL path that all pages must start with
    starting_url_path VARCHAR(128) UNIQUE NOT NULL,
    FOREIGN KEY (course_term_id) REFERENCES course_term(course_term_id)
);

CREATE TABLE IF NOT EXISTS user (
    -- for internal backend code
    user_id INT PRIMARY KEY AUTO_INCREMENT,

    -- for public-facing code
    user_uuid CHAR(36) UNIQUE NOT NULL,

    full_name VARCHAR(64) NOT NULL,
    email VARCHAR(128) UNIQUE NOT NULL,
    hashed_password CHAR(163) NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollment (
    course_id INT NOT NULL,
    user_id INT NOT NULL,
    role INT NOT NULL,
    PRIMARY KEY (course_id, user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS page (
    page_id INT PRIMARY KEY AUTO_INCREMENT,
    page_visibility_setting INT NOT NULL,
    page_content MEDIUMTEXT NOT NULL,
    page_title VARCHAR(256),
    url_path_after_course_path VARCHAR(128) NOT NULL,
    course_id INT NOT NULL,

    -- may be empty if user is deleted
    created_by_user_id INT,

    UNIQUE (url_path_after_course_path, course_id),
    FOREIGN KEY (created_by_user_id) REFERENCES user(user_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE IF NOT EXISTS file (
    file_id INT PRIMARY KEY AUTO_INCREMENT,
    file_uuid CHAR(36) UNIQUE NOT NULL,
    filepath VARCHAR(128) UNIQUE NOT NULL,
    uploaded_by_user_id INT,
    course_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (uploaded_by_user_id) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS page_file_bridge (
    page_id INT,
    file_id INT,
    PRIMARY KEY (page_id, file_id),
    FOREIGN KEY (page_id) REFERENCES page(page_id),
    FOREIGN KEY (file_id) REFERENCES file(file_id)
);

CREATE TABLE IF NOT EXISTS attendance_session (
    attendance_session_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    opening_time DATETIME NOT NULL,
    closing_time DATETIME NOT NULL,

    -- optional user-friendly table
    title VARCHAR(128),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE IF NOT EXISTS attendance_record (
    user_id INT NOT NULL,
    attendance_session_id INT NOT NULL,
    PRIMARY KEY (user_id, attendance_session_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (attendance_session_id) REFERENCES attendance_session(attendance_session_id)
);

-- Triggers
DELIMITER //
DROP TRIGGER IF EXISTS before_insert_trigger;
CREATE TRIGGER before_insert_trigger
    BEFORE INSERT ON user
    FOR EACH ROW
BEGIN
    DECLARE new_uuid CHAR(36);
    REPEAT
        SET new_uuid = UUID();
    UNTIL NOT EXISTS (SELECT 1 FROM user WHERE user.user_uuid = new_uuid)
        END REPEAT;
    SET NEW.user_uuid = new_uuid;
END //
DELIMITER ;

DELIMITER //
DROP TRIGGER IF EXISTS before_insert_trigger_on_file;
CREATE TRIGGER before_insert_trigger_on_file
    BEFORE INSERT ON file
    FOR EACH ROW
BEGIN
    DECLARE new_uuid CHAR(36);
    REPEAT
        SET new_uuid = UUID();
    UNTIL NOT EXISTS (SELECT 1 FROM file WHERE file.file_uuid = new_uuid)
        END REPEAT;
    SET NEW.file_uuid = new_uuid;
END //
DELIMITER ;
