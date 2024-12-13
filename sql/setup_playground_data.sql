-- This script assumes that you've already run setup_schema.sql
-- and have an otherwise blank database

INSERT INTO course_term (title, position_from_top) VALUES ('Spring 2024', 2);
INSERT INTO course_term (title, position_from_top) VALUES ('Fall 2024', 1);

INSERT INTO course (title, user_friendly_class_code, starting_url_path, course_term_id)
VALUES ('Visual Programming', 'CPSC 236', '/cpsc-236-f24', 1);
INSERT INTO course (title, user_friendly_class_code, starting_url_path, course_term_id)
VALUES ('Database Management', 'CPSC 408', '/english/literature', 2);

-- Creates users with the password "12345"
INSERT INTO user (full_name, email, hashed_password)
VALUES ('John Doe', 'john.doe@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Jane Smith', 'jane.smith@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Bob Johnson', 'bob.johnson@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Alice Brown', 'alice.brown@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Charlie Wilson', 'charlie.wilson@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Eva Davis', 'eva.davis@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');
INSERT INTO user (full_name, email, hashed_password)
VALUES ('Frank Miller', 'frank.miller@example.com', 'scrypt:32768:8:1$s9yZxVAUhmWEfmb6$c2738833e6e12be7bb4b536b59957d6f880becdf3235ee21777de77bc3535e82de1336e20064b782fa2b1b65c106eaef5c7328f140ef3dd210ac6224c941c564');

-- Roles
-- 1: student
-- 2: assistant
-- 3: professor
-- Roles 2 and 3 have the ability to edit content
INSERT INTO enrollment (course_id, user_id, role) VALUES (1, 1, 3);
INSERT INTO enrollment (course_id, user_id, role) VALUES (1, 2, 2);
INSERT INTO enrollment (course_id, user_id, role) VALUES (1, 3, 1);
INSERT INTO enrollment (course_id, user_id, role) VALUES (1, 4, 1);
INSERT INTO enrollment (course_id, user_id, role) VALUES (2, 5, 3);
INSERT INTO enrollment (course_id, user_id, role) VALUES (2, 6, 1);
INSERT INTO enrollment (course_id, user_id, role) VALUES (2, 7, 1);

INSERT INTO page (page_visibility_setting, page_content, url_path_after_course_path, course_id, created_by_user_id, page_title)
VALUES (2, '# Home

Discover the art and science of creating immersive games! This course
offers a comprehensive foundation in game design and development, blending
creativity with technical skills.

## What You''ll Learn

- Design Fundamentals: Explore game mechanics, storytelling, and player experience.
- Development Tools: Hands-on experience with industry-standard tools like Unity or Unreal Engine.
- Programming Basics: Learn essential coding for interactive gameplay.
- Collaborative Creativity: Work in teams to bring ideas to life.

Embark on your journey into the exciting world of game development today!

## Next Steps

To edit this page or create a new one, sign in as an assistant or
professor role. Click [New Page] on the left, or [Edit page] on the top of this page.
', '/', 1, 1, 'Home');
