from insta_account import InstagramAccount
import random
from typing import List, Any
import json
import datetime
import pandas as pd

MAX_SESSION_EVENTS = 200
MAX_DAILY_EVENTS = 1000

now = datetime.datetime.now()


class InstabotSession(object):
    def __init__(self, account: InstagramAccount, follower_ratio_upper_bound: float = 1.5, session_type=None):
        self.account = account
        self.events_performed = 0

        # The maximum limit of follower / following before forcing an unfollow session.
        self.follower_ratio_upper_bound = follower_ratio_upper_bound

        # Empty dict showing what this session has done. This will be added to the log.
        self.session_activity = {'date': f"{now.month}_{now.day}_{now.year}", 'followed': [], 'unfollowed': []}

        # TODO(agodfrey) Make this smarter, lol.
        # Session type is F for follow and U for unfollow.
        if session_type is not None:
            self.session_type = session_type
        elif self.follower_ratio_exceeded() or random.randint(1, 2) == 1:
            self.session_type = 'F'
        else:
            self.session_type = 'U'

    def begin(self, tag=None):
        if self.session_type == 'F':
            if tag is None:
                raise ValueError("Tags cannot be none if you want to follow people!")
            self.start_follow_session(tag)
        else:
            self.start_unfollow_session()
        print(f"Finished {self.session_type} session.\nPerformed {self.events_performed} events.")
        self.log_session()

    # TODO(agodfrey) Make log file update one log per user, rather than storing a file per day and overwriting.
    # -> Open file, add new line for each session.
    def log_session(self):
        print(f"Logging session...")
        df = pd.DataFrame([self.session_activity])
        df.to_csv(f"{self.account.login_name}_{now.month}_{now.day}_{now.year}.csv")
        print("Finished logging session...Shutting down.")

    def start_follow_session(self, tag: str):
        ok_status = self.account.get_posts_by_tag(tag)
        if ok_status:
            posts = self.account.get_last_json()['ranked_items']
            for post in posts:
                media_id = post['pk']
                print(f"Media's ID: {media_id}.")
                for liker in self.account.get_people_that_liked(media_id):
                    if self.events_performed >= MAX_SESSION_EVENTS:
                        return None
                    curr_user = liker['pk']
                    if curr_user not in self.account.following and curr_user not in self.account.followers:
                        self.account.follow_user_id(curr_user)
                        self.events_performed += 1
                        self.session_activity['followed'].append(self.account.get_username_by_id(curr_user))
                        print(f"Followed: {self.account.get_username_by_id(curr_user)}:{curr_user}")
                    else:
                        print(f"Did not follow: {self.account.get_username_by_id(curr_user)}:{curr_user}")
        else:
            print("No posts found...Ending session...")
            return None

    def start_unfollow_session(self):
        # TODO(agodfrey) Allow get_valid_id() to be configured / follow guidelines from project doc.
        for id_to_unfollow in self.get_valid_id():
            if self.events_performed >= MAX_SESSION_EVENTS:
                break
            self.account.unfollow_user_id(id_to_unfollow)
            self.session_activity['unfollowed'].append(self.account.get_username_by_id(id_to_unfollow))
            self.events_performed += 1
            print(f"Unfollowed: {self.account.get_username_by_id(id_to_unfollow)}:{id_to_unfollow}")

    def get_valid_id(self):
        whitelist = self.account.whitelist
        for userID in self.account.following:
            if userID not in whitelist and userID not in self.account.followers:
                yield userID

    def follower_ratio_exceeded(self):
        return (self.account.num_followers / self.account.num_following) > self.follower_ratio_upper_bound


def main():
    import credentials
    acc = InstagramAccount(credentials.username, credentials.password)
    session = InstabotSession(acc, follower_ratio_upper_bound=1.5, session_type='U')
    session.begin()
    print(json.dumps(session.session_activity, indent=4))
    acc.logout()


if __name__ == '__main__':
    main()
