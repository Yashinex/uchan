from uchan.lib.tasks.post_task import PostDetails

TEXT = """
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
"""

NAME = 'Name'
SUBJECT = 'Subject'
PASSWORD = 'password'

if __name__ == '__main__':
    i = 0
    while True:
        import uchan

        post_details = PostDetails({}, 'tech', None, TEXT, NAME, SUBJECT, PASSWORD, False, 1)

        uchan.g.posts_service.handle_post(post_details)
        print('posted!' + str(i))
        i += 1